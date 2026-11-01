# Spec Delta

## Purpose

Provides synthetic example cases that demonstrate how the application behaves across the UC-01 flows, using only the normal case operations.

## ADDED Requirements

### Requirement: Demonstration covers the use case
The project SHALL provide a command that creates synthetic example cases for the basic flow H0, each exception flow E1-E6, the T0-T5 event sequence, and BIM delivery for a new building permit.

#### Scenario: Demo run
- **WHEN** the demo command runs against an empty database
- **THEN** one case per scenario exists and each reaches its expected status

#### Scenario: Demo output
- **WHEN** the demo command finishes
- **THEN** it prints each scenario with its case identifier, stage and status

### Requirement: Demo cases are identifiable as synthetic
Every demo case SHALL have a project name marked `[SYNTHETIC]`, and SHALL be created through the same operations as real cases, so that its history is complete.

#### Scenario: Synthetic label
- **WHEN** a client reads a demo case
- **THEN** its project name starts with `[SYNTHETIC]`

#### Scenario: Demo history
- **WHEN** a client reads the history of a demo case
- **THEN** the history shows the same event types a real case would produce
