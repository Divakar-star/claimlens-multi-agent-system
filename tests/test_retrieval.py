"""Retrieval tests.

The load-bearing ones are the hybrid-beats-vector-only cases: at least five
queries where fusion retrieves the correct chunk and vector search alone does
not. If those cannot be found, the policy corpus is not adversarial enough and
Phase 1 needs fixing, not Phase 2. Implemented in Phase 2.
"""
