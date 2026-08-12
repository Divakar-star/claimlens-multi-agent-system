"""Deterministic coverage arithmetic. No LLM, ever.

Why this exists: language models are unreliable at arithmetic and there is no
upside to letting one compute a payout. Deductible application, per-occurrence
limit checks, and the AUTO_DECIDE_MAX_USD ceiling are ordinary Python with unit
tests. The model decides what the policy MEANS; this module decides what the
numbers ARE. See ADR 0004.

Implemented in Phase 3.
"""
