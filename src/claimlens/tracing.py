"""Trace writer: newline-delimited JSON spans, one file per claim.

Why this exists rather than a tracing SaaS: the trace IS the product here. A
reviewer needs to see which model ran, what it cost, which chunks it saw, and
where it failed, without signing up for anything. Field names are kept
OpenTelemetry-compatible (span_id, parent_id, duration_ms) so swapping in a
real OTel exporter is a small change -- see ADR 0001.

Implemented in Phase 3. Span types: llm, retrieval, tool, decision, rate_limit.
"""
