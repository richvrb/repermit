# Proposal

## Why

The LLM only sees paraphrased rules, so it cannot use requirements outside them or point to where a requirement comes from. The source research in `reports/` identified the documents to use, and the project owner chose to index full texts for internal use.

## What Changes

- Add a source register with issuer, date, jurisdiction, amendments and an on/off switch per source.
- Add knowledge cards: reviewed-by-nobody paraphrases that bridge Arabic-only sources to English retrieval.
- Add an ingest command that downloads the sources and builds a local search index outside git and outside the image.
- Retrieve passages per review, filtered by jurisdiction, and leave out superseded articles.
- Let the LLM cite passages, remove citations that were not retrieved, and record the sources per review.
- Show the sources in the interface.

## Capabilities

### New Capabilities

- `knowledge-retrieval`: Indexing sources and retrieving passages for reviews.

### Modified Capabilities

None. This change builds on changes that have not been archived yet.

## Impact

- New `src/repermit/retrieval.py`, `src/repermit/ingest.py`, `src/repermit/packs/sources.yaml` and `src/repermit/packs/cards.yaml`; changes to `api.py`, `llm.py`, `service.py`, `compose.yaml` and the interface.
- Passages from indexed sources are sent to the Anthropic API.
- Full texts stay in the ignored `knowledge/` folder. Internal use only: see the reuse section of the source report.
