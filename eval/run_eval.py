"""Eval driver over the 60-case golden set.

Why it supports --limit and --resume: one full run is roughly 180 LLM requests
(60 cases x 3 agents), which can exhaust a free-tier daily quota. A run
interrupted by the daily cap must be continuable the next day without
re-spending quota. Concurrency is capped at 2 workers for the same reason.

Also supports --baseline: a single-prompt gemini-2.5-flash run with no
retrieval and no agents over the same golden set. That comparison is the
headline number of the README. Implemented in Phase 4.
"""
