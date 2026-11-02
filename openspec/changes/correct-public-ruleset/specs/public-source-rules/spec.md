# Spec Delta

## Purpose

Keeps the public ruleset in line with its sources.

## ADDED Requirements

### Requirement: Rules stay within their authority
A rule derived from one authority's source SHALL apply only to cases of that authority.

#### Scenario: Other authority
- **WHEN** a case falls under another authority
- **THEN** the structural rule of DDA does not apply

### Requirement: Civil Defence applies everywhere
The system SHALL require a Civil Defence NOC under every authority when the modification may affect preventive safety.

#### Scenario: Safety system changed
- **WHEN** a modification changes a safety system
- **THEN** the NOC is required

### Requirement: Ownership goes to a reviewer
The system SHALL escalate a changed unit boundary to a reviewer.

#### Scenario: Boundary moved
- **WHEN** a modification changes a unit boundary
- **THEN** an issue for both owners' consent is raised

### Requirement: Cases keep their rules
The system SHALL keep assessing a case with the pack version it started with.

#### Scenario: New version
- **WHEN** a new pack version is published
- **THEN** existing cases still load with their own version
