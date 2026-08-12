"""LangGraph assembly: router -> retrieve -> analyst -> reviewer -> decide.

Why a graph rather than a chain of function calls: the interesting behaviour is
in the edges -- retry once when grounding fails, route parse failures to
escalation, cap retries at two. A StateGraph makes those transitions explicit
and inspectable instead of buried in try/except blocks. See ADR 0001.

`decide` is a plain function, not an LLM call. Implemented in Phase 3.
"""
