"""Builds the Chroma and BM25 indexes from data/policies/.

Kept as a script rather than lazy index-on-first-request so that image build
time absorbs the cost and the container starts instantly. Implemented in
Phase 2.
"""
