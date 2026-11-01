# Proposal

## Why

BIM delivery is only a format check on new permits: nothing requires a model, no file is read, and modifications ignore BIM altogether. The LLM also reviews only on request, its questions block nothing, and flags it withdraws stay open. A case should be analysed again every time information is added, and it should not move on while information is outstanding.

## What Changes

- Require an IFC design model for new permits and for modifications under the public pack.
- Accept real IFC files, validate them and read their elements. A `design_model` can no longer be registered as metadata alone.
- Compare the proposed model with the approved baseline model, and derive facts for the rules from the changed elements.
- Provide synthetic baseline and proposed IFC models for each AI test case.
- Run a new LLM review whenever information is added to a case that has been reviewed, and pass the model comparison to it.
- Accept one response per round, holding answers to rule questions, answers to AI questions, documents and a note.
- Hold a case while AI questions are open. After the round limit, remaining questions go to the authority.
- **BREAKING** Close an AI flag when a later review explicitly reports the domain as not affected, and record the withdrawal. This replaces the rule that only a resolution closes a flag.

## Capabilities

### New Capabilities

- `bim-models`: Requiring, reading and comparing IFC models.
- `review-rounds`: Repeating analysis, information requests and reassessment.

### Modified Capabilities

None. This change builds on changes that have not been archived yet.

## Impact

- New `src/repermit/bim.py` and `src/repermit/samples.py`; changes to `api.py`, `assessment.py`, `demo.py`, `knowledge.py`, `llm.py`, `service.py`, `state.py`, the packs and the interface.
- New dependency `ifcopenshell`, which enlarges the container image.
- Each round on an AI case is a paid Claude call and takes up to a minute.
- Parsed model data is stored in the event log; the uploaded file itself is not kept.
