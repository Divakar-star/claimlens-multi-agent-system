"""Router agent -- cheap tier (gemini-2.5-flash-lite).

Why a small model here: routing is the highest-frequency call and the lowest-
reasoning one. Putting it on the cheap tier is most of the cost story (ADR
0004). It emits claim_type, severity, needs_deep_analysis, and 2-4 search
queries for retrieval, validated with Pydantic.

Failure handling: on unparseable JSON, retry once with a repair prompt; on a
second failure, escalate with reason router_parse_failure. Never crash the
graph. Implemented in Phase 3.
"""
