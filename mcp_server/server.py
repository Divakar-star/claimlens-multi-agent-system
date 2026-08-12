"""MCP server exposing the deterministic tools over stdio (Phase 6).

Tools: search_policies, evaluate_coverage, get_escalation_queue. Only the
non-LLM parts of the system are exposed, so any MCP client gets the useful
primitives without inheriting this repo's model choices.
"""
