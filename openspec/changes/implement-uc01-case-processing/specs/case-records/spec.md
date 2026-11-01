# Spec Delta

## Purpose

Keeps the project context, design revisions, evidence and approvals of a permit case as versioned records that assessment can rely on.

## ADDED Requirements

### Requirement: Open a case
The system SHALL open a case from a project name, a current design revision and a responsible role defined in the knowledge pack.

#### Scenario: Valid case
- **WHEN** a client opens a case with a project name, revision and known role
- **THEN** the system returns a new case at the initial process stage with status `open`

#### Scenario: Unknown role
- **WHEN** a client opens a case with a role that is not defined
- **THEN** the system rejects the request and creates no case

### Requirement: Submit a design modification
The system SHALL record a modification with a new design revision, change type, description and any disclosed facts, and SHALL make that revision current.

#### Scenario: Modification recorded
- **WHEN** a consultant submits a modification with a new revision
- **THEN** the request and revision are recorded and an assessment runs

#### Scenario: Revision not new
- **WHEN** a modification names the current revision
- **THEN** the system rejects it and records nothing

### Requirement: Register versioned evidence
The system SHALL register documents, assessments and approvals with an identifier, type, domain, status, design revision and optional validity date and facts. Re-registering an identifier SHALL create a new version and retain earlier versions.

#### Scenario: New version retained
- **WHEN** evidence is registered under an existing identifier
- **THEN** the version number increases and the earlier version remains in the history

#### Scenario: Evidence triggers reassessment
- **WHEN** evidence is registered on a case that has a modification
- **THEN** the system reassesses the case

#### Scenario: Evidence before a modification
- **WHEN** evidence is registered on a case without a modification
- **THEN** the evidence is recorded and no assessment runs

### Requirement: New building permits are delivered in BIM
The system SHALL accept design documents for a new building permit case only in a BIM format declared in the knowledge pack, and SHALL reject any other format. The bundled pack SHALL declare IFC. Design modification cases SHALL NOT be subject to this format restriction.

#### Scenario: BIM delivery accepted
- **WHEN** a design document in a declared BIM format is registered on a new building permit case
- **THEN** the document is recorded

#### Scenario: Non-BIM delivery rejected
- **WHEN** a design document in another format, such as PDF, or without a stated format is registered on a new building permit case
- **THEN** the system rejects the request, names the accepted formats and records nothing

#### Scenario: Modification case unaffected
- **WHEN** a design document in PDF is registered on a design modification case
- **THEN** the document is recorded

### Requirement: Unknown cases are not found
The system SHALL respond with a not-found error to any operation on a case that does not exist.

#### Scenario: Unknown case
- **WHEN** a client requests a case identifier that does not exist
- **THEN** the system returns a not-found error
