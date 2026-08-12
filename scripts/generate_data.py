"""Generates the synthetic corpus: 12 policies, 120 claims, 60 golden cases.

Why synthetic: free-tier Gemini may use prompts for training, so no real claim
text can touch the API. Generating the data also lets the corpus be adversarial
on purpose -- cross-referenced policy documents that defeat keyword-only
search, and claims whose narrative contradicts their stated policy_type.

Deterministic from a fixed seed (settings.random_seed). Implemented in Phase 1.
"""
