# Proposal

## Why

RePermit must demonstrate how a permit moves through the process with AI, including requesting and adding information along the way. Today this is only visible through API calls.

## What Changes

- Serve an English demo interface from the service at `/`.
- List the test cases, and let a user start each one from the interface.
- Show the flow of a case as a timeline that can be stepped through and replayed, with the case state at each step.
- Let the LLM ask for information, and show those questions with the system's deficiencies.
- Let a user answer those questions or add free-text information, then have the LLM assess the case again.
- Add endpoints for listing cases, listing and starting test cases, reading the knowledge pack choices, and reading a case at an earlier step.

## Capabilities

### New Capabilities

- `demo-interface`: Following and operating test cases in a browser.

### Modified Capabilities

None. This change builds on `implement-uc01-case-processing` and `add-llm-assessment`, which have not been archived yet.

## Impact

- New file `src/repermit/static/index.html`; changes to `api.py`, `demo.py`, `llm.py`, `service.py` and `store.py`.
- Starting a live test case or re-running a review is a paid Claude call.
