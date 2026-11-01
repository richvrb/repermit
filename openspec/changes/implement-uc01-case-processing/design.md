# Design

## Context

There is no existing code. See proposal.md for motivation and specs for behavior. UC-01 is a controlled, simulated case: there are no real authority integrations and no official rule source, and BR-08 forbids presenting public mappings as official logic.

## Goals / Non-Goals

**Goals:**

- Every UC-01 flow (H0, E1-E6) and the T0-T5 sequence is exercised by an automated test.
- Authorization and holds are enforced in code, independently of how an assessment was reached.

**Non-Goals:**

- Real authentication. Actor roles are supplied in requests because the process is simulated; the stack must not be exposed publicly.
- More than one active modification per case. A new modification replaces the previous one, and facts accumulate per case.
- Schema migration tooling. The single event table is created at startup.

## Decisions

**Event log as the only state.** A single append-only `case_events` table with a unique `(case_id, seq)` constraint. State is a fold over events. This gives BR-07 and E5's "preserve the earlier state" directly, and the unique constraint provides optimistic concurrency. Rejected: mutable tables plus an audit table, which can drift apart.

**Deterministic assessment, no LLM.** Assessment is a pure function of case state, knowledge pack and date. This makes BR-01, BR-03 and E3 ("does not invent a resolving rule") testable. An LLM can later propose facts as evidence through the same inputs, as a separate change, without touching authorization.

**Three-valued rule evaluation.** A condition is true, false or unknown. Unknown produces `potentially_affected` plus an `unknown_fact` deficiency, which implements BR-03 and T2 without special cases.

**Knowledge pack as validated YAML.** Sources, change types, rules, gaps, roles and actions live in one file, loaded at startup and rejected on any integrity error. Rejected: a rule database, which adds admin surface with no current need.

**Autonomy and authorization are separate modules.** `autonomy` looks at risk and `authorization` looks at roles. Execution requires both, so BR-05 holds structurally.

**Materiality by fingerprint.** An assessment fingerprint covers domains, deficiencies and issues. An executed action stores the fingerprint it relied on; a difference at reassessment is material and reverses the stage. Rejected: declaring materiality per evidence type, which cannot detect indirect effects.

**FastAPI + SQLAlchemy Core; SQLite locally, PostgreSQL in containers.** Core is enough for one table. The Compose stack publishes on `127.0.0.1` only because of the simulated authentication.

## Risks / Trade-offs

- [Actor role is client-supplied] → Documented as simulation only; loopback binding in Compose.
- [Synthetic rules could be mistaken for real ones] → Source kind on every applied rule, disclaimer on every assessment.
- [Reversal resets to the initial stage, even if only a later step was affected] → Conservative: all actions are replayed under current evidence.
- [Facts are case-wide, not per element] → Accepted by the single-modification non-goal.
- [State fold grows with events] → Case histories are small; add snapshots only if measured.
