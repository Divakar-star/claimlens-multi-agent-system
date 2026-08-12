"""Evaluation metrics, each a pure function with a precise docstring.

Why definitions matter more than values here: "accuracy" on a triage task is
ambiguous until you say whether over-escalation counts as an error. It does
not, in this system -- escalation recall is weighted above precision because
missing a claim that needed a human is a real harm while over-escalating is
only a cost. Implemented in Phase 4.
"""
