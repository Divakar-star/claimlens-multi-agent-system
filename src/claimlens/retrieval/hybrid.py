"""Reciprocal Rank Fusion over the vector and BM25 indexes.

Why RRF rather than score normalisation: cosine similarity and BM25 scores are
on incomparable scales, and any weighting between them is a hyperparameter
nobody has data to tune. RRF only uses rank, so it needs no calibration --
score(d) = sum over retrievers of 1 / (60 + rank_i(d)).

Implemented in Phase 2. search(query, k=6) returns chunks with provenance:
which retriever found each one, and at what rank.
"""
