"""Reviewer agent -- reasoning tier, deliberately kept ignorant.

Why it does not see the Analyst's reasoning: a reviewer shown the chain of
thought tends to ratify it. This one sees only the claim, the cited chunks, and
the draft decision, and answers three booleans with one-line justifications:
grounding, consistency, completeness. Any false forces escalation regardless of
the Analyst's confidence. Implemented in Phase 3.
"""
