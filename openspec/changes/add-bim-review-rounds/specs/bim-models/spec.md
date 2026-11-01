# Spec Delta

## Purpose

Requires real IFC design models and uses them as evidence.

## ADDED Requirements

### Requirement: Design model required
The system SHALL hold a case of a permit type listed in the pack's `bim_required_for` until a current design model is delivered for its revision.

#### Scenario: No model
- **WHEN** a new permit or a public-pack modification has no design model for its revision
- **THEN** a `missing` deficiency for `design_model` holds the case

#### Scenario: Model delivered
- **WHEN** a valid IFC file is uploaded for the revision
- **THEN** the deficiency closes

### Requirement: Real IFC delivery
The system SHALL accept a design model only as a file that parses as IFC, of at most 50 MB.

#### Scenario: Invalid file
- **WHEN** a file is uploaded that is not valid IFC
- **THEN** the upload is rejected and nothing is recorded

#### Scenario: Metadata only
- **WHEN** a client registers a `design_model` through the evidence endpoint on a case that requires BIM
- **THEN** the request is rejected

### Requirement: Model comparison
The system SHALL compare a proposed model with the baseline model by `GlobalId`, and record the added, removed and changed elements.

#### Scenario: Moved wall
- **WHEN** a wall has a different placement in the proposed model
- **THEN** it is listed as changed

#### Scenario: No baseline
- **WHEN** no baseline model exists
- **THEN** the model is recorded without changes or derived facts

### Requirement: Facts from the model
The system SHALL derive facts only from values stated on changed elements.

#### Scenario: Load-bearing wall changed
- **WHEN** a changed wall has `LoadBearing` true
- **THEN** `load_bearing` is established as true

#### Scenario: Value missing
- **WHEN** a changed element does not state a value
- **THEN** the fact stays unknown

#### Scenario: Model contradicts an answer
- **WHEN** a derived fact differs from an applicant's answer
- **THEN** an `inconsistent_fact` deficiency holds the case

### Requirement: Synthetic models
The system SHALL provide a baseline and a proposed IFC model for each AI test case, and start the case with the baseline registered.

#### Scenario: Sample download
- **WHEN** a client requests a sample model of a test case
- **THEN** a valid IFC file is returned

#### Scenario: Start
- **WHEN** an AI test case starts
- **THEN** its baseline model is registered and the proposed model is still missing
