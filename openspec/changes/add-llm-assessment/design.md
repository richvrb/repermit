# Design

## Context

Assessment is a pure function of case state, pack and date, and materiality compares fingerprints of its output. See proposal.md for motivation. The LLM must fit without breaking either property.

## Goals / Non-Goals

**Goals:**

- The LLM reads and judges each modification, and its result is visible and retained.
- A wrong, manipulated or missing LLM answer can cause an unnecessary escalation, never an unsupported action.

**Non-Goals:**

- Reading drawing or BIM file contents. The LLM sees the modification text and evidence metadata only.
- Tool use or an agent loop. One structured call is enough.
- Evaluating LLM accuracy. This needs a labelled case set, which does not exist yet.

## Decisions

**Review as an event.** The call happens in the service, and the result is stored as `llm_review_recorded`. `assess()` reads it from state and stays pure, so replay and materiality are unaffected. Rejected: calling the LLM inside assessment, which would make every reassessment non-deterministic and paid.

**One-way ratchet.** The rules alone decide domain status. A finding on a domain the rules call `not_affected` becomes an `llm_flag` issue. No finding can reduce a status, and proposed facts never reach rule evaluation. Prompt injection therefore has no path to approval. Rejected: feeding extracted facts into the rules, because one wrong "non-load-bearing" would silently close a safety domain.

**Flags reuse the issue path.** Flags and failures are issues, so they escalate and resolve through the existing authority flow, keyed by revision.

**Structured output with Claude Opus 5.5.** `client.beta.messages.parse` with a Pydantic schema, effort `high` and `fallbacks: "default"`, so a safety-classifier refusal on building terminology is re-run on a fallback model. A final refusal or empty result counts as unavailable.

**Assessor behind a small interface.** The service depends on `review(state, pack)`. Tests use a fake, and `REPERMIT_LLM_PROVIDER=none` disables the LLM.

**Demo stays offline by default.** `python -m repermit.demo` remains free and deterministic; `--llm` adds a live free-text scenario.

## Risks / Trade-offs

- [False flags cause extra escalations] → Accepted: errs towards human review; flags can be resolved.
- [Requests wait on the LLM] → 90-second timeout with one retry, then the case escalates and the review can be re-run.
- [Case text leaves the deployment] → Only modification text and evidence metadata are sent; stated in the README.
- [Review goes stale as evidence arrives] → Rules still react to evidence; a re-run is available on request.
