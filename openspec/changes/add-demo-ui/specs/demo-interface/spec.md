# Spec Delta

## Purpose

Demonstrates in a browser how a permit case moves through the process with AI, and how information is requested and added along the way.

## ADDED Requirements

### Requirement: List and start test cases
The interface SHALL list the test cases with their title, explanation, and whether they call the LLM, and SHALL let a user start one.

#### Scenario: Start a test case
- **WHEN** a user starts a test case
- **THEN** a new `[SYNTHETIC]` case is created and opened

#### Scenario: Every change type is covered
- **WHEN** a user views the test cases that call the LLM
- **THEN** each change type of the public pack appears as an expected type, including boundary cases

#### Scenario: Unknown test case
- **WHEN** a client starts a test case that does not exist
- **THEN** the system returns a not-found error

### Requirement: List started cases
The system SHALL list all cases, newest first, with their project, stage and status.

#### Scenario: Case list
- **WHEN** a client lists cases
- **THEN** each case is returned with its project, stage and status

### Requirement: Show the flow of a case
The interface SHALL show each recorded event of a case as a step in a timeline, labelled with its meaning in the process.

#### Scenario: Timeline
- **WHEN** a user opens a case
- **THEN** the steps are shown in order, including assessments, requests, denials and reversals

### Requirement: Replay a case
The system SHALL return a case as it was at a given event, and the interface SHALL let a user step through and play back the flow. Past states SHALL be read-only.

#### Scenario: Case at an earlier step
- **WHEN** a client reads a case at an earlier event number
- **THEN** the stage, status and assessment are those of that moment

#### Scenario: Invalid step
- **WHEN** a client requests an event number below 1
- **THEN** the system rejects the request

### Requirement: LLM requests information
The LLM review SHALL include the information it needs, each with a question, a domain and a reason.

#### Scenario: Questions shown
- **WHEN** a review contains information requests
- **THEN** the interface shows them as coming from the AI, separately from the deficiencies found by the rules

### Requirement: Add information during processing
The interface SHALL let a user answer open deficiencies, add simulated documents and add free-text information, each recorded as versioned evidence.

#### Scenario: Answer a question
- **WHEN** a user answers an open fact
- **THEN** the answer is recorded as evidence, the case is reassessed and the deficiency closes

#### Scenario: Free-text information
- **WHEN** a user adds free-text information
- **THEN** it is recorded as evidence and included in the next LLM review

#### Scenario: Reassess with the LLM
- **WHEN** a user asks for a new AI assessment
- **THEN** a new review is recorded that takes the added information into account

### Requirement: Operate the process from the interface
The interface SHALL let a user choose a simulated role, request the next action and resolve issues, and SHALL show refusals from the system.

#### Scenario: Refused action
- **WHEN** a user requests an action with a role that lacks permission
- **THEN** the refusal is shown and appears in the timeline

### Requirement: English application
The application SHALL present its interface, test cases, questions, rule texts and LLM output in English.

#### Scenario: Non-English case text
- **WHEN** a case description is written in another language
- **THEN** the LLM review is still written in English

### Requirement: Demo boundaries are visible
The interface SHALL state that the application is a demonstration with synthetic rules and simulated roles, and that it does not issue permits.

#### Scenario: Notice shown
- **WHEN** a user opens the interface
- **THEN** the notice is visible
