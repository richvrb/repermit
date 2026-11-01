# Spec Delta

## Purpose

Determines what a design modification affects, whether the evidence supports the next step, and what must be escalated, without concluding beyond the available evidence.

## ADDED Requirements

### Requirement: Classify affected domains
The system SHALL classify each regulatory domain as `affected`, `potentially_affected` or `not_affected`. A domain whose rule depends on an unknown fact SHALL be `potentially_affected`, never `not_affected`.

#### Scenario: Unknown fact keeps a domain open
- **WHEN** a wall relocation is reported and its fire-boundary role is unknown
- **THEN** the fire-safety domain is `potentially_affected` and the unknown fact is reported as a deficiency

#### Scenario: Known fact closes only its own domain
- **WHEN** evidence shows the wall is non-load-bearing
- **THEN** the structural domain is `not_affected` and the fire-safety domain is unchanged

### Requirement: Conclusions are traceable
The system SHALL list each applied rule with its identifier, source identifier and source kind, so that derived and synthetic rules are distinguishable from authoritative ones.

#### Scenario: Synthetic rule labelled
- **WHEN** a conclusion relies on a synthetic rule
- **THEN** the assessment shows source kind `synthetic` for that rule

### Requirement: Evidence sufficiency
The system SHALL report a deficiency when required evidence is missing, not `current` in status, past its validity date, of unknown revision, or linked to an earlier revision, and SHALL NOT report the case as ready while any deficiency remains.

#### Scenario: Missing evidence
- **WHEN** an affected domain requires evidence that is not registered
- **THEN** the case status is `pending_evidence` and the deficiency names the evidence type

#### Scenario: Evidence received
- **WHEN** valid evidence for the deficiency is registered
- **THEN** the deficiency is cleared and processing resumes

#### Scenario: Evidence past validity
- **WHEN** required evidence has a validity date in the past
- **THEN** a deficiency with code `outdated` is reported

### Requirement: Inconsistent facts stay unresolved
The system SHALL treat a fact with contradictory values across current evidence as unknown and SHALL report it as a deficiency.

#### Scenario: Contradictory evidence
- **WHEN** two current evidence items state different values for the same fact
- **THEN** a deficiency with code `inconsistent_fact` is reported

### Requirement: Revision impact is selective
A design revision SHALL NOT invalidate evidence or approvals outside affected domains. Evidence in an `affected` domain linked to an earlier revision SHALL be marked for revalidation.

#### Scenario: Unaffected approval retained
- **WHEN** a revision does not affect the domain of an existing approval
- **THEN** that approval has impact `retained`

#### Scenario: Stale evidence in an affected domain
- **WHEN** fire-safety evidence is linked to an earlier revision and fire safety is affected
- **THEN** that evidence has impact `revalidate` and the case is held

### Requirement: Rule conflicts are escalated
The system SHALL record an open issue naming the conflicting rules and sources when applicable rules set different values for one parameter, and SHALL NOT select a value itself.

#### Scenario: Conflicting rules
- **WHEN** two applicable rules set different fire ratings
- **THEN** the case status is `escalated` and both rules are listed on the issue

#### Scenario: Authoritative clarification
- **WHEN** the authority role resolves the conflict by selecting a rule and citing a source
- **THEN** the issue closes, the resolution is recorded and assessment resumes

### Requirement: Governance gaps are distinct from retrieval failures
The system SHALL record an issue of kind `process_gap` when a declared gap applies, and of kind `retrieval_gap` when a change type is not covered by the pack. Both SHALL escalate the case until an authority resolves them.

#### Scenario: Process gap
- **WHEN** the facts match a declared process gap
- **THEN** the case status is `escalated` with an issue of kind `process_gap`

#### Scenario: Uncovered change type
- **WHEN** a modification has a change type the pack does not cover
- **THEN** the case status is `escalated` with an issue of kind `retrieval_gap`

### Requirement: Material information reopens progressed work
When a reassessment changes the domains, deficiencies or issues on which an executed action was based, the system SHALL return the case to the initial stage, retaining the earlier history and replanning. Non-material changes SHALL NOT do so.

#### Scenario: Late material evidence
- **WHEN** evidence disclosed after an executed action changes the assessment
- **THEN** the stage returns to the initial stage and a reversal naming the action is recorded

#### Scenario: Non-material evidence
- **WHEN** new evidence leaves domains, deficiencies and issues unchanged
- **THEN** the stage is unchanged and no reversal is recorded
