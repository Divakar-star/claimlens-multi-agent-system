"""Chunking, embedding, and index construction over the policy corpus.

Why two indexes: vector search finds paraphrases but misses exact tokens like
form codes; BM25 does the reverse. The corpus is written so that neither alone
is sufficient -- see ADR 0002.

Why embeddings sit behind an interface: the real embedder pulls in torch and a
90MB model download, which would make every test in the suite slow and
network-dependent. Chunking, id stability and fusion arithmetic have nothing to
do with semantics and are tested against HashEmbedder instead, which is
deterministic and needs nothing. Tests that genuinely require meaning are
marked `requires_model` and run against MiniLMEmbedder in Docker.
"""

from __future__ import annotations

import hashlib
import json
import math
import pickle
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Protocol

from claimlens.config import settings

CHUNK_MANIFEST = "chunks.json"
BM25_PICKLE = "bm25.pkl"
COLLECTION_NAME = "policies"


@dataclass(frozen=True)
class Chunk:
    """One retrievable unit of policy text.

    `chunk_id` is the contract with the rest of the system: the Analyst cites
    it, the golden set asserts it, and `groundedness` checks it exists. It must
    stay stable across index rebuilds, so it is derived from the document slug
    and heading text rather than from position or hash.
    """

    chunk_id: str
    policy_slug: str
    heading: str
    text: str

    @property
    def token_count(self) -> int:
        return len(self.text.split())


def slugify(text: str) -> str:
    """Must match scripts/generate_data.py.slugify -- golden labels depend on it."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def tokenize(text: str) -> list[str]:
    """Lowercased alphanumeric tokens, with form codes kept intact.

    `WD-114` must survive as one token or BM25 loses the exact-match advantage
    that justifies having it, so hyphenated alphanumerics are not split.
    """
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())


def split_long(text: str, max_tokens: int, overlap: int) -> list[str]:
    """Splits an oversized section into overlapping windows.

    Overlap exists so a sentence spanning a boundary is not lost to both
    windows. At this corpus size almost nothing triggers this, but a corpus is
    not a fixed thing and an untested path is a broken path.
    """
    words = text.split()
    if len(words) <= max_tokens:
        return [text]
    step = max_tokens - overlap
    if step <= 0:
        raise ValueError("overlap must be smaller than max_tokens")
    return [
        " ".join(words[i : i + max_tokens])
        for i in range(0, len(words), step)
        if words[i : i + max_tokens]
    ]


def chunk_markdown(markdown: str, policy_slug: str) -> list[Chunk]:
    """Splits a policy document on its level-2 headings.

    The documents are authored one concept per section -- coverage grant,
    exclusions, limits -- so headings are already the right boundary. Content
    before the first heading (title and form code line) is attached to the
    first section rather than dropped, because the form code is exactly the
    token BM25 needs.
    """
    lines = markdown.splitlines()
    sections: list[tuple[str, list[str]]] = []
    preamble: list[str] = []
    current: str | None = None

    for line in lines:
        if line.startswith("## "):
            current = line[3:].strip()
            sections.append((current, []))
        elif current is None:
            preamble.append(line)
        else:
            sections[-1][1].append(line)

    chunks: list[Chunk] = []
    head = " ".join(l.strip() for l in preamble if l.strip() and not l.startswith("#"))

    for i, (heading, body) in enumerate(sections):
        text = " ".join(l.strip() for l in body if l.strip())
        if i == 0 and head:
            text = f"{head} {text}"
        if not text:
            continue
        base_id = f"{policy_slug}#{slugify(heading)}"
        parts = split_long(text, settings.chunk_max_tokens, settings.chunk_overlap_tokens)
        for j, part in enumerate(parts):
            chunk_id = base_id if j == 0 else f"{base_id}-p{j + 1}"
            chunks.append(Chunk(chunk_id, policy_slug, heading, part))
    return chunks


def load_corpus(policies_dir: Path | None = None) -> list[Chunk]:
    """Reads and chunks every policy document, in filename order for stability."""
    directory = policies_dir or settings.policies_dir
    chunks: list[Chunk] = []
    for path in sorted(directory.glob("*.md")):
        chunks.extend(chunk_markdown(path.read_text(encoding="utf-8"), path.stem))
    return chunks


class Embedder(Protocol):
    """Anything that turns text into vectors. Two implementations, see ADR 0002."""

    dimensions: int

    def encode(self, texts: list[str]) -> list[list[float]]: ...


class HashEmbedder:
    """Deterministic bag-of-words hashing. No model, no download, no meaning.

    Exists so the structural half of the test suite runs anywhere in
    milliseconds. It will happily rank an unrelated chunk first, which is fine
    for testing that fusion arithmetic and provenance work, and useless for
    testing retrieval quality. Never use it to make a claim about relevance.
    """

    def __init__(self, dimensions: int = 64) -> None:
        self.dimensions = dimensions

    def encode(self, texts: list[str]) -> list[list[float]]:
        out = []
        for text in texts:
            vec = [0.0] * self.dimensions
            for token in tokenize(text):
                digest = hashlib.md5(token.encode()).digest()
                vec[digest[0] % self.dimensions] += 1.0
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            out.append([v / norm for v in vec])
        return out


class MiniLMEmbedder:
    """sentence-transformers all-MiniLM-L6-v2, CPU only.

    Imported lazily so that importing this module does not drag torch into
    processes that will never embed anything -- the data generator, the fast
    tests, and the API's non-retrieval endpoints.
    """

    def __init__(self, model_name: str | None = None) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name or settings.embedding_model)
        # Renamed in sentence-transformers 5.x; the old name still works but
        # warns. Try the new one first and fall back for older pins.
        getter = getattr(self._model, "get_embedding_dimension", None) or (
            self._model.get_sentence_embedding_dimension
        )
        self.dimensions = getter()

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [list(map(float, v)) for v in self._model.encode(texts, show_progress_bar=False)]


def build_indexes(
    chunks: Iterable[Chunk] | None = None,
    embedder: Embedder | None = None,
) -> dict[str, int]:
    """Builds the Chroma collection and the BM25 index from one chunk list.

    Both are built here, from the same list, so they cannot drift apart. A
    manifest of every chunk is written alongside them: the trace viewer needs
    chunk text without loading Chroma, and `groundedness` needs the set of ids
    that legitimately exist.
    """
    import chromadb
    from rank_bm25 import BM25Okapi

    chunk_list = list(chunks) if chunks is not None else load_corpus()
    if not chunk_list:
        raise RuntimeError(
            "no policy chunks found -- run `make data` before `make index`"
        )
    embed = embedder or MiniLMEmbedder()

    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    settings.bm25_dir.mkdir(parents=True, exist_ok=True)

    texts = [c.text for c in chunk_list]
    ids = [c.chunk_id for c in chunk_list]
    vectors = embed.encode(texts)

    client = chromadb.PersistentClient(path=str(settings.chroma_dir))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:  # noqa: BLE001 - absent collection is the normal first run
        pass
    collection = client.create_collection(COLLECTION_NAME)
    collection.add(
        ids=ids,
        embeddings=vectors,
        documents=texts,
        metadatas=[{"policy_slug": c.policy_slug, "heading": c.heading} for c in chunk_list],
    )

    bm25 = BM25Okapi([tokenize(t) for t in texts])
    with (settings.bm25_dir / BM25_PICKLE).open("wb") as fh:
        pickle.dump({"bm25": bm25, "ids": ids}, fh)

    manifest = {c.chunk_id: asdict(c) for c in chunk_list}
    (settings.chroma_dir / CHUNK_MANIFEST).write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )

    return {"chunks": len(chunk_list), "dimensions": embed.dimensions}


def load_manifest() -> dict[str, dict]:
    """Chunk metadata without touching Chroma. Used by tracing and groundedness."""
    path = settings.chroma_dir / CHUNK_MANIFEST
    if not path.exists():
        raise FileNotFoundError(f"{path} missing -- run `make index`")
    return json.loads(path.read_text(encoding="utf-8"))
