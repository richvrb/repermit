# Design

## Context

See proposal.md for motivation. Rules stay deterministic and the LLM stays advisory: it can hold a case, but it cannot release one or establish a fact.

## Decisions

### Model facts are evidence

Comparing two models is deterministic, so facts derived from it enter the rules like any other evidence. A fact is derived only when the changed elements state a value. Without a value the fact stays unknown and the question stays open. A difference with an applicant's answer is an `inconsistent_fact`, which the applicant resolves by answering again or uploading a corrected model.

| Fact | True when a changed element | False when all changed elements |
|---|---|---|
| `load_bearing` | is a column or beam, or has `LoadBearing` true | are non-structural or have `LoadBearing` false |
| `fire_compartment_boundary` | has a `FireRating` | are finishes or have `FireRating` `NONE` |
| `facade_change` | has `IsExternal` true | are finishes or have `IsExternal` false |

Elements are matched by `GlobalId`, and compared on class, name, placement and property values. Without a baseline there is no comparison and no derived facts.

### Rounds

A response is one command: its evidence, the review and the reassessment are one atomic write. This gives one paid call per round rather than one per answer. Every other route that adds information also triggers a review, so a case can never progress on a review that predates its evidence. Cases that were never reviewed, such as the fixed test cases, stay rule-only.

### Open AI questions

AI questions become `ai_question` deficiencies, so they hold the case until a new review drops them. The LLM could keep asking forever, so after `max_review_rounds` completed reviews on a revision, remaining questions become one `llm_flag` issue for the authority.

### Withdrawing flags

The earlier sticky-flag rule produced 17 stale flags out of 21 in a live run. A flag now closes on an explicit `not_affected` from a later completed review, or once the rules themselves cover its domain. A domain that is merely missing from the review stays flagged, and so does every flag after a failed review. Withdrawals are recorded in the assessment.

### The review sees what the rules ask

The prompt receives established facts and the previous findings, and is told not to repeat what the rules already ask for. This keeps AI questions to what can change the outcome, with at most five per round.

### Storage

Only the parsed model goes in the event log, with the file's hash. Upload size is limited to 50 MB. Element snapshots stay out of case views and prompts.

## Risks

- The comparison reads declared properties, not geometry. A wrong or incomplete model gives wrong facts.
- `FireRating` `NONE` is a demo convention, not an IFC standard value.
- An applicant's text can persuade the LLM to withdraw a flag. The authority's approval remains the control.
- BIM for modifications is a product requirement. The sources show a narrower duty.
- The public pack has no rules for new buildings, so a new permit on that pack escalates as not covered.
