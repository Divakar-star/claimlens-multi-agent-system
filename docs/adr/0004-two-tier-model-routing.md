# 0004. Two model tiers, and no arithmetic in the model

## Status

Accepted

## Context

Three LLM calls per claim, at 60 golden cases per eval run, is roughly 180
requests -- enough that model choice is a real cost decision rather than a
rounding error. The three calls are not equally hard. Routing is
classification: read a narrative, name the claim type, guess severity, propose
search queries. Coverage analysis and review require reading retrieved policy
prose and reasoning about exclusions. Spending the same per-token rate on all
three prices the cheap work at the expensive rate.

The second, sharper problem is arithmetic. A payout is a deductible
subtraction, a per-occurrence limit comparison, and a threshold check against
`AUTO_DECIDE_MAX_USD`. Language models produce plausible arithmetic, which is
worse than obviously wrong arithmetic, and the failure is silent. There is no
benefit to letting the model do it: the inputs are structured numbers.

## Decision

Two tiers. `gemini-2.5-flash-lite` runs the router. `gemini-2.5-flash` runs the
analyst and the reviewer. Both are on the Gemini free tier, so the repo runs at
zero real cost, and `config.py` pins published paid-tier per-million rates so
the eval harness can report a *notional* cost per claim.

All arithmetic moves to `tools/coverage_rules.py`: plain Python, no LLM, unit
tested. The analyst receives its computed numbers as tool output and reasons
about coverage language only. The final `decide` step is likewise a plain
function, not a model call.

## Consequences

### Positive

- The highest-frequency call runs on the cheapest model, which is most of the
  cost delta measured in the Phase 7 writeup.
- Payout arithmetic is deterministic, testable, and identical on every run;
  arithmetic bugs surface in `pytest`, not in a metric.
- The dollar ceiling that gates autonomy is enforced in code the model cannot
  talk its way past. This is what makes "bounded autonomy" more than a label.

### Negative

- Two model names to keep in sync in config, prompts, and the cost table; a
  model deprecation now breaks two paths.
- The cheap router is the most likely source of misclassification, and a bad
  `search_queries` list degrades retrieval for every downstream stage. Phase 7
  measures whether the saving is worth it rather than assuming so.
- Notional cost is not real cost, and must be labelled as such everywhere it
  appears or it becomes an invented number.

### Rejected alternatives

- **`gemini-2.5-flash` for all three agents.** Simpler and the accuracy ceiling
  for this design. Kept as configuration 1 in the Phase 7 comparison rather
  than discarded, so the tradeoff is measured instead of asserted.
- **Flash-Lite for router and reviewer, Flash only for the analyst.** Cheaper
  still, but the reviewer is the last line of defence before an auto-decision
  and degrading it trades a real-world harm for a cost saving. Measured as
  configuration 3 in Phase 7; not the default.
- **Let the model compute the payout and validate it afterwards.** Rejected:
  writing the validator means writing the deterministic calculator anyway, at
  which point the model call is pure cost and pure risk.
- **Gemini Pro tier.** Rejected outright -- restricted to paid accounts as of
  1 April 2026, which breaks the zero-cost constraint.
