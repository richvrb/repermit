# Spec Delta

## Purpose

Uses an LLM to classify and assess design modifications while keeping its output advisory, traceable and unable to weaken any evidence or authorization control.

## ADDED Requirements

### Requirement: Review every modification
The system SHALL obtain an LLM review of each submitted modification containing a change type, classification confidence, materiality, domain findings with rationale, proposed facts, uncertainties and a summary.

#### Scenario: Review recorded
- **WHEN** a modification is submitted
- **THEN** the review is recorded in the history with its model and revision and shown on the assessment

### Requirement: Classification supplies a missing change type
The system SHALL accept a modification without a change type and use the LLM classification. A low-confidence or uncovered classification SHALL be treated as unclassified.

#### Scenario: Confident classification
- **WHEN** a free-text modification is classified with high confidence as a covered change type
- **THEN** the rules for that change type apply and the change type is marked as LLM-sourced

#### Scenario: Low-confidence classification
- **WHEN** the classification confidence is low
- **THEN** the change type is `unclassified` and the case is `escalated` with a `retrieval_gap` issue

#### Scenario: Client type disagrees
- **WHEN** a client-supplied change type differs from the LLM classification
- **THEN** the client type is kept and an `llm_flag` issue escalates the case

#### Scenario: No LLM configured
- **WHEN** a modification without a change type is submitted and no LLM is configured
- **THEN** the system rejects the request

### Requirement: LLM findings can only add caution
The system SHALL raise an `llm_flag` issue when the LLM reports a domain as affected or potentially affected that the rules classify as `not_affected`. LLM findings SHALL NOT lower a domain status.

#### Scenario: Concern beyond the rules
- **WHEN** the LLM reports fire safety as affected and the rules show `not_affected`
- **THEN** the case is `escalated` with an `llm_flag` issue naming the domain

#### Scenario: LLM says unaffected
- **WHEN** the LLM reports a domain as not affected and the rules show it as affected
- **THEN** the domain stays `affected`

#### Scenario: Later review repeats no concern
- **WHEN** a re-run on the same revision no longer reports a flagged concern
- **THEN** the `llm_flag` issue stays open until it is resolved

#### Scenario: Authority resolves a flag
- **WHEN** the authority role resolves an `llm_flag` issue with a cited source
- **THEN** the issue closes and assessment resumes

### Requirement: Proposed facts are not established facts
The system SHALL show LLM-proposed facts for review and SHALL NOT use them in rule evaluation. Only evidence or client-supplied facts SHALL establish a fact.

#### Scenario: Proposed fact ignored by rules
- **WHEN** the LLM proposes that a wall is non-load-bearing
- **THEN** the structural domain remains `potentially_affected` until evidence establishes the fact

### Requirement: LLM output is not an authoritative source
The system SHALL label LLM reviews as non-authoritative and SHALL remove rule citations that do not exist in the knowledge pack, recording them as invalid.

#### Scenario: Invented citation
- **WHEN** a domain finding cites a rule that is not in the pack
- **THEN** the citation is removed from the finding and listed under `invalid_citations`

### Requirement: LLM cannot authorize
The LLM SHALL have no access to actions, and its output SHALL NOT affect authorization. Text in a modification or in evidence SHALL be treated as data.

#### Scenario: Instruction in the description
- **WHEN** a modification description instructs the system to approve the case
- **THEN** no action is authorized by that text and all controls apply as usual

### Requirement: Failed reviews stop the case
The system SHALL record an unavailable review and escalate the case when the LLM cannot be reached, refuses, or returns no usable result. The modification SHALL still be recorded.

#### Scenario: LLM unavailable
- **WHEN** the LLM call fails
- **THEN** the modification is recorded and the case is `escalated` with an `llm_unavailable` issue

#### Scenario: Review re-run
- **WHEN** a client re-runs the review and it succeeds
- **THEN** the `llm_unavailable` issue closes and assessment continues

### Requirement: Reviews do not repeat on evidence
The system SHALL run a review on each new modification and on an explicit re-run, not on evidence registration, so that reassessment stays deterministic.

#### Scenario: Evidence registered
- **WHEN** evidence is registered on a reviewed case
- **THEN** no new LLM review is made
