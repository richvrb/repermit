# Proposal

## Why

A yes or no from the applicant currently counts as an established fact, and a document is only a checkbox. Information must be proven by documents, and the application must assess whether a document contains what it should.

## What Changes

- **BREAKING** On the public pack, open facts are requested as documents. Only opening facts can be answered directly.
- Accept real PDF uploads and read their text.
- Define per document type what it must contain and which facts it can prove.
- Let the LLM report per checklist item, and let code decide whether a document is complete.
- A reviewer confirms each fact read from a complete document before the rules use it.
- Provide synthetic PDFs per test case, including incomplete versions.

## Capabilities

### New Capabilities

- `document-evidence`: Requesting, assessing and confirming documentary proof.

### Modified Capabilities

None. This change builds on changes that have not been archived yet.

## Impact

- New `src/repermit/documents.py`; changes to `samples.py`, `api.py`, `assessment.py`, `knowledge.py`, `llm.py`, `service.py`, `state.py`, the pack and the interface.
- `pypdf` becomes a runtime dependency.
- Document text is sent to the Anthropic API, and the text is stored in the event log.
- Pack version `dubai-public-2026.4`, with a limit of four rounds.
