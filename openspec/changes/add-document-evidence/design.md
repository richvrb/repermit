# Design

## Context

See proposal.md for motivation. The LLM may read and assess, but it still cannot establish a fact on its own.

## Decisions

### Checklists live in the pack

Each document type lists `must_contain` and `proves`. These lists are interpretations: the public sources rarely say what a document must hold. A reviewer or expert should correct them.

### The LLM reports, code decides

The review answers per checklist item whether it is present and where. Code marks a document complete only if it is the expected type, matches the case and has every item. An item the LLM leaves out counts as missing.

### One review per round

Uploads are stored without an LLM call. Submitting the round sends the unreviewed documents in one review, so a round stays one paid call. Reviewed documents are not sent again.

### Facts need a person

A fact read from a complete document becomes a `fact_to_confirm` deficiency showing value, quote and document. Only a resolution role can confirm or decline it. A confirmed fact is recorded as evidence, without a new LLM call. Facts are limited to the type's `proves` list.

### Statements do not prove

Text answers stay as context for the LLM but close nothing. An AI question names the document it wants, and closes only when a later review drops it. Opening facts, such as the competent authority, can still be chosen directly.

### Text extraction only

Only PDFs with a text layer are read. A scan yields no text and is marked unreadable, so a signature or stamp in an image cannot be seen. The check that a stamp is present relies on text, so this is a limit of the demo.

## Risks

- A forged or wrongly dated document can pass: nothing is verified with the issuer.
- Text in a document can try to steer the LLM. It is data, the verdict is code, and a person confirms the facts.
- Reviewers can confirm without reading; the interface shows the quote to help.
