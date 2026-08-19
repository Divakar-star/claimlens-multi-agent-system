"""Measures where each retriever ranks the chunk that should govern a query.

Why this exists: the Phase 2 claim is that hybrid retrieval beats vector-only
on this corpus. The first attempt at testing that used invented keyword-salad
queries, and vector search found six of them unaided -- which said more about
the queries than about retrieval. This script reports the rank each retriever
assigns the expected chunk, over queries written the way the Router will
actually phrase them, so the test cases can be chosen from evidence rather than
from intuition.

Rank, not presence, because presence at an arbitrary k hides the interesting
part: a chunk moving from rank 14 to rank 2 is the fusion working, even if both
retrievers technically "found" it at depth 20.

Usage (inside the container, where the model lives):
    python scripts/retrieval_report.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from claimlens.retrieval.hybrid import HybridRetriever  # noqa: E402
from claimlens.retrieval.index import MiniLMEmbedder  # noqa: E402

DEPTH = 20

# Queries in the register the Router emits: short natural-language phrases
# derived from a claimant narrative, not keyword salad. `expected` is the chunk
# that actually governs the question -- verified against the corpus text, not
# assumed.
CANDIDATES: list[tuple[str, str, str]] = [
    # -- cross-reference chases: the answer is in a document the claim was not filed under
    ("car submerged in flood water is it covered",
     "flood-exclusion#interaction-with-other-coverages",
     "flood damage to a vehicle is payable, but only FX-0090 s3 says so"),
    ("vehicle sat in rising water overnight engine damage",
     "auto-comprehensive#what-is-covered",
     "flood-to-vehicle lands in comprehensive, not collision"),
    ("sewage backed up through the floor drain",
     "water-damage-endorsement#what-is-covered",
     "backup is the endorsement, not the dwelling form"),
    ("rain pooled against the foundation and seeped into the basement",
     "water-damage-endorsement#exclusions",
     "surface water seepage is excluded even where a drain was overwhelmed"),
    ("stolen camera gear used for my photography business",
     "business-equipment-rider#what-is-covered",
     "business property above the HP-1155 sub-limit needs the rider"),
    ("tow truck after a crash who pays",
     "auto-collision#interaction-with-other-coverages",
     "collision towing is in AC-2210, not the roadside form"),
    ("hire car while my vehicle is being repaired",
     "rental-reimbursement#what-is-covered",
     "substitute transport is a separate form"),
    ("visitor injured at my house wants medical bills paid",
     "medical-payments#what-is-covered",
     "no-fault medical is MP-0450, not the liability form"),

    # -- defined terms with counter-intuitive meanings
    ("is a slow leak behind the shower sudden and accidental",
     "homeowners-dwelling#definitions",
     "the definition is what decides it"),
    ("water came in from the street and the drain backed up at the same time",
     "water-damage-endorsement#interaction-with-other-coverages",
     "efficient proximate cause governs mixed causation"),

    # -- exact-token lookups: form codes and figures
    ("what does form WD-114 cover",
     "water-damage-endorsement#coverage-summary",
     "form code appears in the preamble of the first chunk"),
    ("FX-0090 does the flood exclusion apply to my car",
     "flood-exclusion#interaction-with-other-coverages",
     "form code plus the vehicle carve-out"),
    ("AC-2210 deductible per occurrence",
     "auto-collision#deductible-and-limits", "form code in a numeric section"),
    ("named storm deductible percentage",
     "homeowners-dwelling#deductible-and-limits", "defined term, exact phrase"),
    ("jewelry limit on a contents claim",
     "homeowners-personal-property#what-is-covered", "sub-limit figure"),
    ("how many roadside call outs per year",
     "roadside-assistance#exclusions", "the cap lives in the exclusions"),
    ("maximum days for a rental car claim",
     "rental-reimbursement#what-is-covered", "thirty day cap"),
    ("time limit for medical payments claims",
     "medical-payments#exclusions", "three year bar is an exclusion"),

    # -- clear-exclusion lookups
    ("damage during a track day at a circuit",
     "auto-collision#exclusions", "racing exclusion"),
    ("keys left in the car when it was stolen",
     "auto-comprehensive#exclusions", "keys exclusion"),
]


def rank_of(ranking: list[str], target: str) -> str:
    return str(ranking.index(target) + 1) if target in ranking else "-"


def main() -> None:
    retriever = HybridRetriever(embedder=MiniLMEmbedder())

    print(f"rank of the expected chunk, depth {DEPTH}  ('-' = not retrieved)\n")
    print(f"{'vec':>4} {'bm25':>5} {'hyb':>4}  query")
    print("-" * 78)

    wins_at_6, wins_at_3, rank_gains, misses = 0, 0, 0, []
    for query, expected, _why in CANDIDATES:
        vec = retriever.vector_search(query, DEPTH)
        bm25 = retriever.keyword_search(query, DEPTH)
        hyb = [c.chunk_id for c in retriever.search(query, k=DEPTH)]

        v, b, h = rank_of(vec, expected), rank_of(bm25, expected), rank_of(hyb, expected)
        print(f"{v:>4} {b:>5} {h:>4}  {query}")

        v_i = vec.index(expected) + 1 if expected in vec else 999
        h_i = hyb.index(expected) + 1 if expected in hyb else 999
        if h_i <= 6 and v_i > 6:
            wins_at_6 += 1
        if h_i <= 3 and v_i > 3:
            wins_at_3 += 1
        if h_i < v_i:
            rank_gains += 1
        if h_i == 999:
            misses.append((query, expected))

    total = len(CANDIDATES)
    print("-" * 78)
    print(f"hybrid finds it in top 6 where vector-only does not : {wins_at_6}/{total}")
    print(f"hybrid finds it in top 3 where vector-only does not : {wins_at_3}/{total}")
    print(f"hybrid ranks it strictly higher than vector-only    : {rank_gains}/{total}")
    if misses:
        print("\nnot retrieved by hybrid at all (check the expectation):")
        for query, expected in misses:
            print(f"  {query!r} -> {expected}")


if __name__ == "__main__":
    main()
