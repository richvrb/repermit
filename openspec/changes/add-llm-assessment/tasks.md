# Tasks

## 1. LLM review

- [x] 1.1 Add the review schema, Claude assessor and citation checks; verify with `tests/test_llm.py`
- [x] 1.2 Record reviews as events and add classification to the service; verify with `tests/test_llm.py`

## 2. Controls

- [x] 2.1 Add `llm_flag` and `llm_unavailable` issues and the one-way ratchet; verify with `tests/test_llm.py`

## 3. Interface and deployment

- [x] 3.1 Add the re-run endpoint, configuration and Compose variables; verify with `tests/test_llm.py` and `docker compose config`
- [x] 3.2 Add the `--llm` demo and update `README.md`; verify the documented command runs

## 4. Integration

- [x] 4.1 Run a live free-text case against the Claude API; verify a recorded review and the expected case status
- [x] 4.2 Rebuild the Compose stack and run a live review in the container; verify the readiness endpoint and a recorded review
