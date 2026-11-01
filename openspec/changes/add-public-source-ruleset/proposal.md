# Proposal

## Why

The live AI cases rest on invented rules, and one change type gives the LLM almost nothing to classify. Public Dubai sources define change types, permit duties and document requirements that can replace them, as far as those sources are reachable.

## What Changes

- Add a knowledge pack derived from public Dubai sources, with a source and section for every rule.
- Classify modifications into the Dubai Building Code change types.
- Record the knowledge pack on each case, so that fixed test cases stay on the synthetic pack.
- Ask for one unknown fact per rule at a time, using questions from the pack.
- Give the LLM rule text, change type definitions and fact names.
- Add a source analysis that records what was read, what could not be reached and what is not covered.

## Capabilities

### New Capabilities

- `public-source-rules`: Rules derived from public sources, with provenance and explicit gaps.

### Modified Capabilities

None. This change builds on `implement-uc01-case-processing`, `add-llm-assessment` and `add-demo-ui`, which have not been archived yet.

## Impact

- New file `src/repermit/packs/dubai_public.yaml` and `docs/source-analysis.md`.
- Changes to `knowledge.py`, `assessment.py`, `state.py`, `service.py`, `control.py`, `llm.py`, `api.py`, `demo.py` and the interface.
- Live cases use the new pack by default. Cases opened earlier stay on the synthetic pack.
