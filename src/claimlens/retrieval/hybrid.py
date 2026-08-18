"""Reciprocal Rank Fusion over the vector and BM25 indexes.

Why RRF rather than weighted score fusion: cosine similarity and BM25 scores
live on incomparable scales, and any weighting between them is a
hyperparameter with no labelled retrieval data to tune it against. RRF uses
only rank, so it needs no calibration:

    score(d) = sum over retrievers of 1 / (60 + rank_i(d))

Why provenance is returned with every chunk: when the Analyst cites the wrong
clause, the trace has to distinguish "the right chunk was never retrieved" from
"the right chunk was retrieved at rank 2 and ignored". Those are different
bugs with different fixes, and without provenance they look identical.

See ADR 0002.
"""

from __future__ import annotations

import pickle
from dataclasses import dataclass, field
from typing import Callable, Sequence

from claimlens.config import settings
from claimlens.retrieval.index import (
    BM25_PICKLE,
    COLLECTION_NAME,
    Embedder,
    MiniLMEmbedder,
    load_manifest,
    tokenize,
)

CANDIDATE_DEPTH = 20  # per retriever, before fusion

# A ranking is an ordered list of chunk ids, best first.
Ranking = Sequence[str]
Retriever = Callable[[str, int], Ranking]


@dataclass
class RetrievedChunk:
    """A fused result, carrying enough context to audit the retrieval."""

    chunk_id: str
    text: str
    score: float
    provenance: dict[str, int] = field(default_factory=dict)

    @property
    def found_by(self) -> list[str]:
        return sorted(self.provenance)

    def cite(self) -> str:
        return f"[{self.chunk_id}]"


def reciprocal_rank_fusion(
    rankings: dict[str, Ranking],
    k: int = settings.rrf_k,
) -> list[tuple[str, float, dict[str, int]]]:
    """Fuses several ranked lists into one. Pure function, no I/O.

    `k` damps the influence of top ranks: with k=60, rank 1 contributes 1/61
    and rank 2 contributes 1/62, so a chunk found by both retrievers at
    mediocre rank outranks one found brilliantly by a single retriever. That is
    the intended behaviour -- agreement between two different methods is
    stronger evidence than confidence within one.

    Returns (chunk_id, score, {retriever: rank}) sorted by score descending,
    ties broken by chunk id so results are deterministic.
    """
    scores: dict[str, float] = {}
    provenance: dict[str, dict[str, int]] = {}

    for retriever_name, ranking in rankings.items():
        for position, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + position)
            provenance.setdefault(chunk_id, {})[retriever_name] = position

    return sorted(
        ((cid, score, provenance[cid]) for cid, score in scores.items()),
        key=lambda row: (-row[1], row[0]),
    )


class HybridRetriever:
    """Vector + BM25 search over the persisted indexes.

    Both retrievers are injectable. In production they are Chroma and
    rank_bm25; in tests they are stubs, which is how the fusion path is tested
    without a model, a download, or a database.
    """

    def __init__(
        self,
        embedder: Embedder | None = None,
        vector_search: Retriever | None = None,
        keyword_search: Retriever | None = None,
    ) -> None:
        self._embedder = embedder
        self._vector_search = vector_search
        self._keyword_search = keyword_search
        self._manifest: dict[str, dict] | None = None
        self._bm25 = None
        self._bm25_ids: list[str] = []
        self._collection = None

    # -- lazily loaded backends ------------------------------------------------

    @property
    def manifest(self) -> dict[str, dict]:
        if self._manifest is None:
            self._manifest = load_manifest()
        return self._manifest

    def _collection_handle(self):
        if self._collection is None:
            import chromadb

            client = chromadb.PersistentClient(path=str(settings.chroma_dir))
            self._collection = client.get_collection(COLLECTION_NAME)
        return self._collection

    def _bm25_handle(self):
        if self._bm25 is None:
            path = settings.bm25_dir / BM25_PICKLE
            if not path.exists():
                raise FileNotFoundError(f"{path} missing -- run `make index`")
            with path.open("rb") as fh:
                payload = pickle.load(fh)
            self._bm25 = payload["bm25"]
            self._bm25_ids = payload["ids"]
        return self._bm25

    # -- the two retrievers ----------------------------------------------------

    def vector_search(self, query: str, depth: int = CANDIDATE_DEPTH) -> list[str]:
        if self._vector_search is not None:
            return list(self._vector_search(query, depth))
        if self._embedder is None:
            self._embedder = MiniLMEmbedder()
        vector = self._embedder.encode([query])[0]
        result = self._collection_handle().query(query_embeddings=[vector], n_results=depth)
        return list(result["ids"][0])

    def keyword_search(self, query: str, depth: int = CANDIDATE_DEPTH) -> list[str]:
        if self._keyword_search is not None:
            return list(self._keyword_search(query, depth))
        bm25 = self._bm25_handle()
        scores = bm25.get_scores(tokenize(query))
        ordered = sorted(
            range(len(scores)), key=lambda i: (-scores[i], self._bm25_ids[i])
        )
        return [self._bm25_ids[i] for i in ordered[:depth] if scores[i] > 0]

    # -- the public entry point ------------------------------------------------

    def search(self, query: str, k: int = 6) -> list[RetrievedChunk]:
        """Runs both retrievers to CANDIDATE_DEPTH, fuses, returns the top k."""
        rankings = {
            "vector": self.vector_search(query, CANDIDATE_DEPTH),
            "bm25": self.keyword_search(query, CANDIDATE_DEPTH),
        }
        fused = reciprocal_rank_fusion(rankings)
        manifest = self.manifest
        out: list[RetrievedChunk] = []
        for chunk_id, score, provenance in fused[:k]:
            entry = manifest.get(chunk_id)
            out.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=entry["text"] if entry else "",
                    score=score,
                    provenance=provenance,
                )
            )
        return out

    def search_many(self, queries: list[str], k: int = 6) -> list[RetrievedChunk]:
        """Fuses across several queries at once.

        The Router emits two to four search queries per claim. Fusing all their
        rankings together, rather than searching separately and concatenating,
        means a chunk that several queries agree on rises -- which is the same
        agreement argument RRF rests on in the first place.
        """
        rankings: dict[str, Ranking] = {}
        for i, query in enumerate(queries):
            rankings[f"vector:{i}"] = self.vector_search(query, CANDIDATE_DEPTH)
            rankings[f"bm25:{i}"] = self.keyword_search(query, CANDIDATE_DEPTH)
        fused = reciprocal_rank_fusion(rankings)
        manifest = self.manifest
        return [
            RetrievedChunk(
                chunk_id=cid,
                text=manifest.get(cid, {}).get("text", ""),
                score=score,
                provenance=prov,
            )
            for cid, score, prov in fused[:k]
        ]
