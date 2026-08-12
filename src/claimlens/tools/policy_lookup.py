"""Policy-document lookup by id or slug, wrapping the retrieval layer.

Why separate from retrieval/: the agents and the MCP server both need a stable,
tool-shaped interface over the corpus, and neither should depend on Chroma
internals. Implemented in Phase 3, re-exported over MCP in Phase 6.
"""
