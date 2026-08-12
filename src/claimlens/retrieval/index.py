"""Builds the two indexes the hybrid retriever fuses.

Why two: vector search finds paraphrases but misses exact tokens like policy
ids and defined terms; BM25 does the reverse. The policy corpus is written with
cross-references between documents specifically so that neither retriever alone
is sufficient.

Implemented in Phase 2. Chunks by markdown heading, splits anything over 500
tokens with 80-token overlap, and assigns each chunk a stable id of the form
<policy-slug>#<heading-slug> so citations are checkable against the corpus.
"""
