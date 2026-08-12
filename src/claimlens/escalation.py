"""Human-in-the-loop queue logic.

Why escalation is a first-class module: the system's central claim is that it
knows when NOT to decide. Escalation reasons are machine-readable so
escalation precision and recall can be measured, and human overrides are stored
alongside the draft decision because disagreements are the most valuable
training signal the system produces. Implemented in Phase 5.
"""
