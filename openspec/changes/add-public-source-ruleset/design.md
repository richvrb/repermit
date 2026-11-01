# Design

## Context

See proposal.md for motivation and `docs/source-analysis.md` for the sources. The UAE Fire and Life Safety Code and Dubai Municipality's service documents could not be retrieved, so the pack has real gaps.

## Goals / Non-Goals

**Goals:**

- Every rule can be traced to a section of a source that was actually read.
- A missing source leads to an escalation, never to an assumed rule.

**Non-Goals:**

- Numerical design checks, which need drawing or BIM data.
- Complete coverage of Dubai regulation. BR-08 still applies.

## Decisions

**All rules are `derived`.** The sources are official, but each rule is a paraphrase and trigger chosen for this system, so `authoritative` would overstate them. Triggers the source leaves open, such as when a Civil Defence NOC applies, are stated as interpretation in the rule text.

**Pack version on the case.** `case_opened` records the pack, and the service resolves it per case. Rules can then change without altering past assessments. Rejected: one global pack, which would break the fixed scenarios and reinterpret old cases.

**DDA rules apply only to DDA cases.** The service cards are DDA documents. Applying them to Dubai Municipality cases would present another authority's list as binding, so those cases raise a gap.

**One unknown fact per rule.** A pack with many facts would otherwise ask everything at once. Asking the first unknown creates a natural conversation, and domain status remains `potentially_affected` until resolved.

**Questions live in the pack.** Facts differ per pack, so the deficiency carries its question and options, and the interface needs no fact-specific code.

## Risks / Trade-offs

- [Rules are outdated when sources change] → Retrieval date per source; the DDA cards date from 2021.
- [Local Order 3/1999 has been amended] → Only read in its base text; recorded as a limitation.
- [A paraphrase misstates a source] → Section reference per rule for checking; legal review is still required before real use.
- [Dubai Municipality cases always escalate] → Accepted, because that list could not be read.
