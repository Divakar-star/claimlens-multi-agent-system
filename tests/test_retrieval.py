"""Retrieval tests, in two tiers.

Fast tier (no model, no network): chunk id stability, tokenisation of form
codes, fusion arithmetic, provenance, and the guarantee that every chunk the
golden set asserts actually exists in the corpus.

Model tier (`requires_model`): the load-bearing claim of Phase 2 -- that hybrid
retrieval beats vector-only on this corpus. Those cases need real embeddings,
because proving hybrid beats a hash-based fake embedder would prove nothing.
"""

from __future__ import annotations

import pytest

from claimlens.retrieval.hybrid import HybridRetriever, reciprocal_rank_fusion
from claimlens.retrieval.index import (
    Chunk,
    HashEmbedder,
    chunk_markdown,
    slugify,
    split_long,
    tokenize,
)

# ---------------------------------------------------------------- fast tier --


def test_chunk_ids_are_slug_and_heading():
    md = "# Title\n\n**Form XX-1234**\n\n## Coverage Summary\n\nBody text here.\n"
    chunks = chunk_markdown(md, "demo-policy")
    assert [c.chunk_id for c in chunks] == ["demo-policy#coverage-summary"]


def test_preamble_is_attached_not_dropped():
    """The form code lives above the first heading and BM25 needs it."""
    md = "# Title\n\n**Form XX-1234** | Policy `POL-1`\n\n## Coverage Summary\n\nBody.\n"
    chunks = chunk_markdown(md, "demo")
    assert "XX-1234" in chunks[0].text


def test_chunk_ids_are_stable_across_calls(corpus):
    from claimlens.retrieval.index import load_corpus

    assert [c.chunk_id for c in corpus] == [c.chunk_id for c in load_corpus()]


def test_chunk_ids_are_unique(corpus):
    ids = [c.chunk_id for c in corpus]
    assert len(ids) == len(set(ids))


def test_every_golden_chunk_exists_in_corpus(golden_cases, chunk_ids):
    """Guards the citation_recall metric: a typo in a label would silently
    depress the score forever, and look like a retrieval failure."""
    missing = {
        chunk
        for case in golden_cases
        for chunk in case["required_policy_chunks"]
        if chunk not in chunk_ids
    }
    assert not missing, f"golden set references non-existent chunks: {sorted(missing)}"


def test_tokenizer_keeps_form_codes_intact():
    """WD-114 must survive as one token or BM25 loses its whole advantage."""
    assert "wd-114" in tokenize("See Form WD-114 for details")
    assert "fx-0090" in tokenize("Form FX-0090, Section 2")


def test_slugify_matches_generator():
    assert slugify("Interaction With Other Coverages") == "interaction-with-other-coverages"
    assert slugify("Deductible and Limits") == "deductible-and-limits"


def test_split_long_overlaps():
    words = " ".join(str(i) for i in range(250))
    parts = split_long(words, max_tokens=100, overlap=20)
    assert len(parts) > 1
    first_tail = parts[0].split()[-20:]
    second_head = parts[1].split()[:20]
    assert first_tail == second_head


def test_split_long_leaves_short_text_alone():
    assert split_long("a b c", max_tokens=100, overlap=20) == ["a b c"]


def test_oversized_section_gets_part_suffixes():
    body = " ".join(["word"] * 900)
    chunks = chunk_markdown(f"## Big Section\n\n{body}\n", "demo")
    assert len(chunks) > 1
    assert chunks[0].chunk_id == "demo#big-section"
    assert chunks[1].chunk_id == "demo#big-section-p2"


def test_rrf_arithmetic_is_exact():
    fused = reciprocal_rank_fusion({"a": ["x"], "b": ["x"]}, k=60)
    assert fused[0][0] == "x"
    assert fused[0][1] == pytest.approx(2 / 61)


def test_rrf_prefers_agreement_over_single_retriever_confidence():
    """Two retrievers agreeing at rank 2 beats one shouting at rank 1.

    This is the property that makes fusion worth doing, so it is asserted
    rather than assumed.
    """
    fused = reciprocal_rank_fusion(
        {"vector": ["loud", "agreed"], "bm25": ["other", "agreed"]}
    )
    assert fused[0][0] == "agreed"


def test_rrf_records_provenance_with_ranks():
    fused = reciprocal_rank_fusion({"vector": ["a", "b"], "bm25": ["b"]})
    provenance = {cid: prov for cid, _, prov in fused}
    assert provenance["b"] == {"vector": 2, "bm25": 1}
    assert provenance["a"] == {"vector": 1}


def test_rrf_is_deterministic_on_ties():
    a = reciprocal_rank_fusion({"v": ["z", "y"], "b": ["y", "z"]})
    b = reciprocal_rank_fusion({"v": ["z", "y"], "b": ["y", "z"]})
    assert [row[0] for row in a] == [row[0] for row in b]


def test_search_fuses_injected_retrievers():
    """The whole search path, with both backends stubbed out.

    The manifest is seeded directly rather than monkeypatched onto the class,
    which would leak into every later test in the session.
    """
    retriever = HybridRetriever(
        vector_search=lambda q, d: ["chunk-a", "chunk-b"],
        keyword_search=lambda q, d: ["chunk-b", "chunk-c"],
    )
    retriever._manifest = {
        "chunk-a": {"text": "A"}, "chunk-b": {"text": "B"}, "chunk-c": {"text": "C"}
    }
    results = retriever.search("anything", k=3)
    assert [r.chunk_id for r in results] == ["chunk-b", "chunk-a", "chunk-c"]
    assert results[0].found_by == ["bm25", "vector"]
    assert results[0].text == "B"


def test_hash_embedder_is_deterministic():
    e = HashEmbedder()
    assert e.encode(["Form WD-114"]) == e.encode(["Form WD-114"])


def test_chunk_token_count():
    assert Chunk("a#b", "a", "B", "one two three").token_count == 3


# --------------------------------------------------------------- model tier --

# Each case is a query whose governing chunk is reachable through an exact
# token -- a form code, a defined term, a specific figure -- that embeddings
# handle badly. The corpus was written to make these possible; if fewer than
# five hold, the corpus is not adversarial enough and Phase 1 is what needs
# fixing, not Phase 2.
HYBRID_ADVANTAGE_CASES = [
    ("Form FX-0090 Section 3 covered auto", "flood-exclusion#interaction-with-other-coverages"),
    ("WD-114 sump pump per-occurrence limit", "water-damage-endorsement#deductible-and-limits"),
    ("Named Storm Deductible two percent", "homeowners-dwelling#deductible-and-limits"),
    ("BE-7720 serial number schedule sixty days", "business-equipment-rider#conditions-and-claims-handling"),
    ("MP-0450 funeral expenses three years", "medical-payments#what-is-covered"),
    ("RR-0310 thirty days daily rate", "rental-reimbursement#what-is-covered"),
    ("HP-1155 jewelry sub-limit 2,000", "homeowners-personal-property#what-is-covered"),
    ("RA-0075 four occurrences twelve-month period", "roadside-assistance#what-is-covered"),
    ("AC-2210 nearest qualified repair facility towing", "auto-collision#what-is-covered"),
    ("Efficient Proximate Cause definition", "water-damage-endorsement#definitions"),
]

MIN_HYBRID_WINS = 5


@pytest.fixture(scope="module")
def live_retriever():
    from claimlens.retrieval.index import MiniLMEmbedder

    return HybridRetriever(embedder=MiniLMEmbedder())


@pytest.mark.requires_model
def test_hybrid_beats_vector_only_on_at_least_five_cases(live_retriever):
    """The load-bearing Phase 2 assertion.

    Reported as an aggregate rather than ten separate tests because the claim
    being made is about the retrieval strategy, not about any individual query:
    a single case flipping as the model or corpus changes is noise, five cases
    disappearing is the strategy failing. The breakdown is printed either way.
    """
    wins, losses = [], []
    for query, expected in HYBRID_ADVANTAGE_CASES:
        hybrid_ids = [c.chunk_id for c in live_retriever.search(query, k=6)]
        vector_ids = live_retriever.vector_search(query, 6)
        if expected in hybrid_ids and expected not in vector_ids:
            wins.append(query)
        else:
            losses.append((query, expected, expected in hybrid_ids, expected in vector_ids))

    print(f"\nhybrid advantage: {len(wins)}/{len(HYBRID_ADVANTAGE_CASES)} cases")
    for query in wins:
        print(f"  WIN   {query}")
    for query, expected, in_hybrid, in_vector in losses:
        print(f"  no    {query!r} -> {expected} (hybrid={in_hybrid}, vector={in_vector})")

    assert len(wins) >= MIN_HYBRID_WINS, (
        f"only {len(wins)} cases where hybrid beat vector-only; need "
        f"{MIN_HYBRID_WINS}. The policy corpus is not adversarial enough -- "
        f"fix Phase 1, not Phase 2."
    )


@pytest.mark.requires_model
def test_search_returns_ids_not_blobs(live_retriever):
    """Citations must be checkable, so retrieval returns ids with text attached
    rather than anonymous text."""
    results = live_retriever.search("water damage in the basement", k=6)
    assert results
    assert all(r.chunk_id and "#" in r.chunk_id for r in results)
    assert all(r.provenance for r in results)


@pytest.mark.requires_model
def test_search_many_fuses_multiple_queries(live_retriever):
    """The Router emits 2-4 queries; all of them must contribute to one ranking."""
    results = live_retriever.search_many(
        ["sump pump backup", "Form FX-0090 surface water"], k=6
    )
    assert results
    retrievers = {name.split(":")[0] for r in results for name in r.provenance}
    assert retrievers <= {"vector", "bm25"}
    assert len(results) <= 6
