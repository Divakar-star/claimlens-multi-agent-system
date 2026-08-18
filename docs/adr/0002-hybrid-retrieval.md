# 0002. Fuse vector and keyword retrieval with Reciprocal Rank Fusion

## Status

Accepted

## Context

The Analyst agent can only reason about policy text it is given, and every
citation it produces is checked against the corpus by the `groundedness`
metric. Retrieval quality therefore sets a ceiling on the whole system: a claim
whose governing clause was never retrieved cannot be decided correctly, only
guessed correctly.

The corpus is deliberately hostile to any single retrieval method. Policy
documents refer to each other by form code -- `WD-114`, `FX-0090`, `AC-2210` --
and those codes are exactly the tokens embeddings handle worst: short,
arbitrary, with no semantic neighbourhood. A query containing `FX-0090` is
close, in embedding space, to every other policy document and specifically
close to none.

The reverse failure is just as easy to produce. A claimant writes "water came
up the street and sat in my basement", the governing text says "Surface Water,
including water that pools against the foundation". No content word overlaps.
BM25 scores that pair near zero; an embedding model gets it immediately.

Worse, the two failures interact. The claim above is filed under a water damage
endorsement, but the clause that decides it lives in the *flood exclusion*
document, which the endorsement cross-references by form code. Answering it
correctly requires the semantic match to find the topic and the lexical match
to follow the cross-reference.

Combining two rankings requires a comparable scale, and cosine similarity and
BM25 scores have none. Cosine sits in a narrow band near the top of its range;
BM25 is unbounded above and corpus-dependent. Any fixed weighting between them
is a hyperparameter, and there is no labelled retrieval data here to tune one
against -- the golden set labels decisions, not relevance judgements.

## Decision

Run both retrievers independently for their top 20, then fuse by Reciprocal
Rank Fusion:

    score(d) = sum over retrievers of 1 / (60 + rank_i(d))

Return the top 6 with provenance recorded per chunk: which retriever found it,
and at what rank.

Chunk on markdown headings, since the documents are authored with one concept
per section, splitting any chunk over 500 tokens with 80 tokens of overlap.
Every chunk carries a stable id of the form `<policy-slug>#<heading-slug>`.

Put embeddings behind a two-line `Embedder` interface with two
implementations: `MiniLMEmbedder` (the real one) and `HashEmbedder` (a
deterministic bag-of-words hash, no model, no download).

## Consequences

### Positive

- RRF uses only rank, so nothing needs calibrating and neither retriever can
  dominate through score scale. It is also two lines of arithmetic, which
  matters when the alternative is a tuned weighting nobody can justify.
- Recording provenance makes retrieval debuggable: when the Analyst cites the
  wrong clause, the trace shows whether the right chunk was retrieved and
  ignored, or never retrieved at all. Those are different bugs.
- Heading-based chunk ids are human-readable, stable across index rebuilds, and
  checkable against the corpus, which is what makes hallucinated citations
  detectable rather than merely suspected.
- The `Embedder` interface splits the test suite in two. Chunking, id
  stability, fusion arithmetic and provenance are tested with no model, no
  download and no network, so they run in CI in seconds. Only the tests that
  genuinely require semantics pay for the model.

### Negative

- RRF discards score magnitude entirely. A chunk both retrievers rank first
  with overwhelming confidence scores identically to one they rank first
  narrowly, so the fused score cannot be read as a relevance estimate and is
  not exposed as one.
- The constant 60 is inherited from the original RRF paper, not tuned here.
  With top-20 lists it flattens the contribution of ranks 10 to 20 to nearly
  nothing, which is acceptable at this corpus size and would need revisiting at
  scale.
- Two indexes must be kept in sync. `make index` rebuilds both from the same
  chunk list, so they cannot drift, but a partial rebuild would corrupt the
  pairing silently.
- `HashEmbedder` produces vectors with no semantic content whatsoever. It is
  useful only for structural tests and would be actively misleading if a
  retrieval-quality test were ever run against it. The model-backed tests are
  marked `requires_model` specifically so this line cannot be crossed by
  accident.

### Rejected alternatives

- **Vector search alone.** The default choice, and the one this ADR exists to
  argue against. It cannot follow a cross-reference by form code, which is the
  single most common way this corpus hides the governing clause.
- **BM25 alone.** Cheaper, no model, no image bloat, and it handles the form
  codes perfectly. It fails on every paraphrase, and claimants paraphrase
  constantly -- that is what a claim narrative is.
- **Weighted score fusion after min-max normalisation.** Would preserve score
  magnitude, which RRF throws away. Rejected because normalisation is
  query-dependent (min-max over what population?) and the weight would be
  picked by feel. RRF's ordering-only assumption is weaker and therefore safer.
- **A cross-encoder reranker over the fused list.** Almost certainly better
  quality, and the obvious next step if `citation_recall` turns out to be the
  binding constraint in Phase 4. Rejected for now because it adds a second
  model, roughly doubles retrieval latency, and would be tuning before there is
  any measurement to tune against.
