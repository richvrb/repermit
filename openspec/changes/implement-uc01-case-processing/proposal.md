# Proposal

## Why

RePermit exists only as a use case specification (UC-01 v1.0, `../requirements/`). Consultants need a running service that assesses a building-permit design modification, adapts when information changes, and never acts beyond the evidence or its authorization.

## What Changes

- Add a Python HTTP service that implements UC-01: basic flow H0 and exception flows E1-E6.
- Add a versioned case record for design revisions, evidence and approvals.
- Require BIM delivery of design documents for new building permit cases.
- Add a regulatory knowledge pack with provenance. The first pack is explicitly synthetic and is not official BPS logic (BR-08).
- Add deterministic impact and evidence assessment, planning, autonomy evaluation and mandatory authorization.
- Add an append-only case history covering evidence, decisions, authorization outcomes and state transitions.
- Add container images and a Compose stack for deployment.

## Capabilities

### New Capabilities

- `case-records`: Opening cases and registering design modifications, evidence and approvals as versioned records.
- `regulatory-knowledge`: Loading rules, sources, roles and process actions with provenance labels.
- `impact-assessment`: Determining affected domains, evidence sufficiency, conflicts, governance gaps and materiality of new information.
- `action-control`: Planning next actions, evaluating autonomy, enforcing authorization, and holding or executing simulated actions.
- `case-history`: Retaining and exposing the traceable history of a case.
- `container-deployment`: Running the service as containers with configuration and health checks.
- `demo-cases`: Synthetic example cases that demonstrate the UC-01 flows.

### Modified Capabilities

None.

## Impact

- New code under `src/repermit/`, tests under `tests/`, and container files at the project root.
- New dependencies: FastAPI, Uvicorn, SQLAlchemy, psycopg, PyYAML.
- Out of scope: issuing permits, certifying compliance, real government integrations, a web front end, and LLM-based reasoning.
