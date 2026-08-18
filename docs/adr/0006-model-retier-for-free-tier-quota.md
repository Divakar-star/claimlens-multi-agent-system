# 0006. Retier onto 3.1 Flash Lite after measuring the actual free-tier quota

## Status

Accepted. Supersedes the model assignment in ADR 0004; the rest of 0004 stands.

## Context

ADR 0004 assigned `gemini-2.5-flash-lite` to the router and `gemini-2.5-flash`
to the analyst and reviewer, on the assumption that both sit on a free tier
with workable limits. That assumption was never checked against the account
actually running this project, because the published documentation and the real
per-project quota are different things.

The measured limits, read off the AI Studio rate-limit page on 2026-08-18:

| Model | RPM | TPM | RPD |
|---|---|---|---|
| gemini-3.1-flash-lite | 15 | 250K | **500** |
| gemini-2.5-flash | 5 | 250K | **20** |
| gemini-2.5-flash-lite | 10 | 250K | **20** |
| gemini-3-flash | 5 | 250K | 20 |

One eval run over the 60-case golden set is 180 requests: 60 router calls plus
120 analyst and reviewer calls. Against a 20 RPD ceiling on both 2.5 tiers, the
router alone needs three days and the full run needs nine. Phase 7 compares
three configurations, so a complete measurement pass would take roughly a
month of quota. The design in ADR 0004 is not slow on this account -- it is
unrunnable, and an eval harness that cannot be run produces no numbers, which
is the one outcome task.md rules out.

`gemini-3.1-flash-lite` is the only model here with a daily quota exceeding a
single eval run, by a factor of nearly three.

## Decision

Default both `MODEL_REASONING` and `MODEL_CHEAP` to `gemini-3.1-flash-lite`.
Keep them as two separate settings rather than collapsing them into one, so the
two-tier configuration remains a one-line `.env` change and the graph code
continues to route by tier rather than by model name.

Reserve the 20 RPD of `gemini-2.5-flash` for Phase 7, where a 10-case
stratified subset costs exactly one day of quota (10 cases x 2 reasoning calls)
and answers the question ADR 0004 assumed: does the more expensive tier
actually buy accuracy on this task?

Rate-limiter defaults are set below the measured values (12 RPM against a
measured 15, 450 RPD against 500) so that a burst does not walk into a 429.

## Consequences

### Positive

- An eval run completes in one day with quota to spare, so the regression gate
  in Phase 4 is a gate rather than an aspiration.
- Reported numbers come from real runs. Nothing in the README has to be
  hedged as "not yet measured".
- The tier abstraction survives intact. Anyone with a paid account can restore
  ADR 0004's assignment by editing two environment variables.
- The Phase 7 writeup gets a sharper question: not "which tier is cheaper" but
  "what does the expensive tier buy, measured on the sample size the quota
  permits".

### Negative

- The headline cost comparison weakens. With one model doing all three roles,
  the per-claim cost delta between agentic and baseline is driven by call count
  alone, not by call count and price. Notional cost per claim rises, because
  3.1 Flash Lite ($0.25/$1.50 per 1M tokens) is dearer than 2.5 Flash Lite
  ($0.10/$0.40) for the routing work.
- The Phase 7 reasoning-tier comparison rests on 10 cases. That is enough to
  see a large effect and nowhere near enough to see a small one, and the
  writeup must say so rather than reporting a percentage as if it were solid.
- These quotas are account-specific and have changed repeatedly during 2026.
  This ADR will go stale; the `.env.example` comment carries the measurement
  date so the next reader knows how old the numbers are.

### Rejected alternatives

- **Keep the 2.5 tiers and shrink the golden set to 10 cases.** Preserves
  literal compliance with the model table at the cost of the eval, where every
  metric would move in 10-point steps and escalation recall would be computed
  over three or four cases. The measurement is the point of the project; the
  model names are not.
- **Keep the 2.5 tiers and accept nine-day eval runs.** Defensible if the repo
  were finished and static. It is not: the regression gate exists to catch
  changes, and a gate with a nine-day cycle catches nothing.
- **Enable billing.** Removes the constraint entirely for a few dollars, and is
  what a working team would do. Rejected because zero-cost operation is an
  explicit constraint in task.md, and because handling a real quota ceiling is
  a more interesting thing to demonstrate than paying to make it disappear.
- **Mix tiers: 3.1 Flash Lite router, 2.5 Flash analyst and reviewer.** Still
  120 requests per run against 20 RPD. Six days. No better.
