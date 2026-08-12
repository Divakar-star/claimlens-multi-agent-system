"""Coverage Analyst agent -- reasoning tier (gemini-2.5-flash).

Why this agent does not do arithmetic: it calls coverage_rules.evaluate(), a
deterministic tool, for deductibles, limits, and the auto-decide ceiling. Its
job is to read retrieved policy language and produce a draft decision whose
rationale cites chunk ids inline, so groundedness can be measured rather than
assumed. Implemented in Phase 3.
"""
