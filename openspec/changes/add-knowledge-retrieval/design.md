# Design

## Context

See proposal.md for motivation. Retrieved text is advisory like the rest of the LLM review: it can raise a question or a flag, but rules and evidence still decide.

## Decisions

### SQLite FTS5 index

About 3,000 passages fit a keyword index in one file. It needs no service, is built once, and is mounted read-only into the container. Vector search can follow if retrieval tests show keyword search is not enough.

### Filter before ranking

Jurisdiction and the source switch are checked per passage. A source for `dda` never reaches a `dm` case. While the authority is unknown only sources for all authorities are used. Superseded articles are marked at ingest and never returned, so Local Order 3/1999 art. 4 cannot appear as current text.

### Cards next to full text

Arabic sources cannot be found with English queries, and some sources are unavailable. Cards are short English paraphrases in `cards.yaml`, always marked unverified until an expert confirms them. A search returns at most three cards and five passages, with at most three from one source.

### Citations

The review returns citations by passage id. Ids that were not retrieved are removed and recorded as invalid, as with rule ids. The event stores id, source, reference, link and a short excerpt, so a review stays traceable without the full text in the log.

## Risks

- Keyword search misses synonyms, so retrieval is measured with test questions.
- Text in sources is data. The prompt says not to follow instructions in it.
- PDF extraction of an 843-page document loses tables and layout, so page references are approximate.
- Reuse terms limit this to internal use. Switching off a source takes effect without rebuilding the index.
