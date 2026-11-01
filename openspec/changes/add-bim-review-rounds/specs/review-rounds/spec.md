# Spec Delta

## Purpose

Repeats analysis, information requests and reassessment until nothing is outstanding.

## ADDED Requirements

### Requirement: Reassess on new information
The system SHALL run a new LLM review in the same write whenever information is added to a case that has an LLM review.

#### Scenario: Evidence added
- **WHEN** evidence or a model is added to a reviewed case
- **THEN** a new review is recorded before the case can progress

#### Scenario: Case without review
- **WHEN** evidence is added to a case that never had a review
- **THEN** no LLM call is made

### Requirement: Response per round
The system SHALL accept one response holding fact answers, answers to AI questions, documents and a note, and SHALL record them together with one new review.

#### Scenario: Response
- **WHEN** an applicant submits a response
- **THEN** each part is recorded as evidence and exactly one review follows

#### Scenario: Empty response
- **WHEN** a response holds nothing
- **THEN** it is rejected

#### Scenario: Document not requested
- **WHEN** a response names a document that is not an open deficiency
- **THEN** it is rejected and nothing is recorded

### Requirement: Open AI questions hold the case
The system SHALL treat each information request of the latest review as a deficiency until a later review no longer asks it.

#### Scenario: Question open
- **WHEN** the latest review contains an information request
- **THEN** an `ai_question` deficiency holds the case

#### Scenario: No more questions
- **WHEN** a later review contains no information requests
- **THEN** the deficiencies close and the case can progress

#### Scenario: Round limit
- **WHEN** a review at the round limit still contains questions
- **THEN** they become one issue that only the authority can resolve

### Requirement: Withdrawn flags
The system SHALL close an AI flag when a later completed review explicitly reports its domain as not affected, and SHALL record the withdrawal.

#### Scenario: Explicit withdrawal
- **WHEN** a later review reports a flagged domain as `not_affected`
- **THEN** the flag closes and the assessment lists it as withdrawn

#### Scenario: Domain left out
- **WHEN** a later review does not mention a flagged domain
- **THEN** the flag stays open

#### Scenario: Failed review
- **WHEN** a later review is unavailable
- **THEN** the flag stays open

### Requirement: Rounds shown
The interface SHALL show the current round and collect all open questions, documents and models in one place.

#### Scenario: Next round
- **WHEN** a user submits the response
- **THEN** the new assessment appears as the next round in the timeline
