# Proposal

## Why

Modifications arrive as free text, and fixed rules alone cannot read them or notice concerns the rules do not cover. An LLM must classify and assess each modification, without weakening BR-01, BR-03 and BR-05.

## What Changes

- Classify and assess every design modification with Claude.
- Allow a modification to be submitted without a change type; the LLM classification supplies it.
- Escalate when the LLM raises a concern the rules do not show. The LLM can add caution but cannot remove it, approve anything or authorize an action.
- Escalate instead of concluding when the LLM is unavailable, refuses or returns an unusable answer.
- Retain each review as case history, and allow a review to be re-run.

## Capabilities

### New Capabilities

- `llm-assessment`: LLM classification and assessment of design modifications, and the limits on how that output is used.

### Modified Capabilities

None. This change builds on `implement-uc01-case-processing`, which has not been archived yet.

## Impact

- New module `src/repermit/llm.py`, changes to `service.py`, `assessment.py`, `state.py`, `api.py` and `demo.py`.
- New dependency: `anthropic`. New configuration for the provider, model and API key.
- Modification text and evidence metadata are sent to the Anthropic API, and each review has a cost.
