# Tasks

## 1. Project setup

- [x] 1.1 Add `pyproject.toml`, package skeleton and ignore files; verify `pip install -e .[dev]` succeeds

## 2. Knowledge

- [x] 2.1 Implement pack loading and integrity validation with the synthetic pack; verify with `tests/test_knowledge.py`

## 3. Case model and persistence

- [x] 3.1 Implement the event store and state fold; verify with `tests/test_store.py`, including the concurrent write conflict

- [x] 3.2 Add a permit type to cases and enforce BIM formats on new building permit cases; verify with the BIM scenarios in `tests/test_api.py`

## 4. Assessment

- [x] 4.1 Implement three-valued rules, domains, evidence checks, impact, conflicts and gaps; verify with `tests/test_assessment.py`

## 5. Action control

- [x] 5.1 Implement planning, autonomy and authorization; verify with `tests/test_flows.py`
- [x] 5.2 Implement the case service with reassessment, materiality reversal and autonomous execution; verify E4 and E5 tests in `tests/test_flows.py`

## 6. API

- [x] 6.1 Implement the HTTP API and health endpoints; verify with `tests/test_flows.py` and `tests/test_api.py`
- [x] 6.2 Add the H0, E1-E6 and T0-T5 flow tests; verify all pass with `pytest`

- [x] 6.3 Add the `repermit.demo` command with synthetic cases for H0, E1-E6, T0-T5 and BIM delivery; verify with `tests/test_demo.py`

## 7. Containers

- [x] 7.1 Add `Dockerfile`, `compose.yaml` and `.env.example`; verify `docker compose config` succeeds
- [x] 7.2 Document running, testing and deployment in `README.md`; verify the documented commands run

## 8. Integration

- [x] 8.1 Build and start the Compose stack and run the H0 flow against PostgreSQL; verify the readiness endpoint and a completed case
- [x] 8.2 Verify `openspec validate implement-uc01-case-processing --strict` passes

## Workflow follow-up

- Archive the change with `/opsx:archive` once it has been reviewed.
