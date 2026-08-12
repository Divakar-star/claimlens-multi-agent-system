# 0001. Orchestrate the agents with LangGraph, and trace them ourselves

## Status

Accepted

## Context

The triage flow is not a straight line. Three model calls are involved, and the
interesting behaviour lives in the transitions between them: the router can
emit unparseable JSON and must be retried once then escalated; the reviewer can
reject the analyst's grounding, which sends the claim back for exactly one more
attempt; a rate-limit error must escalate rather than crash. Any of this can be
written with plain function calls and try/except, but then the control flow is
scattered across the handlers and cannot be drawn, tested, or explained.

Separately, this system's output is a decision that a human may have to audit.
That means every model call needs to be recorded with its model, token counts,
duration, and the chunks it saw. The obvious answer is a hosted tracing
product, but a hiring engineer cloning this repo will not sign up for one, and
a demo that degrades without a SaaS key is a worse demo.

## Decision

Use LangGraph's `StateGraph` for orchestration, with a single `TypedDict` state
object threaded through every node, and write our own tracing to
newline-delimited JSON at `traces/<trace_id>.jsonl` using a context manager.
Span field names follow OpenTelemetry conventions (`span_id`, `parent_id`,
`duration_ms`).

## Consequences

### Positive

- Retries, escalation edges, and the retry cap are declared as edges rather
  than buried in exception handlers, so `graph.py` reads as the architecture
  diagram.
- The state object is one place to look for what each agent contributes.
- Traces are inspectable with `cat` and `jq`, and the trace viewer is a Jinja2
  template over the same file, so no data is hidden behind a vendor UI.
- Because the field names are OTel-compatible, swapping in a real exporter is a
  change to `tracing.py` alone.

### Negative

- LangGraph is a dependency with its own release cadence and a state model that
  a reader may have to learn; for a three-node graph it is arguably heavier
  than needed.
- Hand-rolled tracing means no sampling, no aggregation, and no UI beyond what
  we build. Fine at 60 golden cases, wrong at production volume.

### Rejected alternatives

- **Plain Python functions with explicit retry loops.** Fewer dependencies and
  perfectly adequate for three nodes. Rejected because the retry and escalation
  edges are the part of this system worth showing, and inline control flow
  makes them invisible; also loses checkpointing if the graph later grows.
- **LangChain agents / AgentExecutor.** Rejected because the tool-calling loop
  it provides is the wrong shape here: this system's sequence is fixed by
  design, and bounded autonomy means we do not want the model choosing what to
  call next.
- **OpenTelemetry SDK with an OTLP exporter from the start.** Rejected for
  Phase 0 because it requires a collector to be useful, which violates the
  "clone and run in five minutes" constraint. Kept as a cheap future option by
  matching its field names now.
