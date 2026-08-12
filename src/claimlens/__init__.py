"""ClaimLens: a bounded-autonomy claims triage system.

Why this package exists: insurance triage is a task where a fully autonomous
LLM is the wrong answer -- the cost of a wrong auto-denial is borne by a
claimant, not by the operator. Every module here exists to keep the model
inside an envelope: deterministic arithmetic, retrieved-and-cited policy text,
an independent review pass, and a hard dollar ceiling above which no automated
decision is allowed at all.
"""

__version__ = "0.1.0"
