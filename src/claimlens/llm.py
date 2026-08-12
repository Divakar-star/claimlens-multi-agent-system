"""Gemini client wrapper, mock client, rate limiting, and cost accounting.

Why this exists: free-tier quota is enforced across three dimensions at once
(RPM, TPM, RPD) and an unhandled 429 is the most common way a demo like this
breaks in front of a reviewer. Rate limiting therefore lives in the same place
as the client rather than being sprinkled through the agents, and every 429 is
recorded as a trace span so the failure is visible rather than silent.

Implemented in Phase 3. Planned contents:
  - RateLimitExceeded: typed error the graph routes to escalation.
  - TokenBucket: per-model-tier limiter sized from settings.rpm_for().
  - DailyBudget: RPD counter persisted in SQLite, refuses calls past budget.
  - GeminiClient: google-genai wrapper, exponential backoff with jitter
    (1, 2, 4, 8, 16s), returns text plus token counts.
  - MockLLMClient: deterministic canned responses so the full graph, the tests,
    and the Docker demo run with no API key and no network.
"""
