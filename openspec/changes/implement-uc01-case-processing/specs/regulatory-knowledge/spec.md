# Spec Delta

## Purpose

Supplies the rules, sources, roles and process actions used for assessment, with provenance that keeps authoritative, derived and synthetic material distinct.

## ADDED Requirements

### Requirement: Every rule has provenance
The system SHALL refuse to load a knowledge pack containing a rule or gap that does not reference a declared source, or a source without a kind of `authoritative`, `derived` or `synthetic`.

#### Scenario: Rule without a declared source
- **WHEN** a pack contains a rule that references an undeclared source
- **THEN** loading fails and the service does not start

### Requirement: Process definition is unambiguous
The system SHALL refuse to load a pack in which an action references an undeclared role or stage, or in which a stage has more than one outgoing action.

#### Scenario: Two actions from one stage
- **WHEN** a pack declares two actions from the same stage
- **THEN** loading fails

### Requirement: Knowledge pack is identified
The system SHALL record the pack version on every assessment.

#### Scenario: Pack version on assessment
- **WHEN** an assessment is recorded
- **THEN** it states the version of the pack used

### Requirement: Public mappings are not presented as official logic
The system SHALL include in every assessment a statement that it is not a government permit, an engineering certification or a competent-authority decision, and that its rules do not represent complete Dubai Municipality/BPS logic.

#### Scenario: Disclaimer on assessment
- **WHEN** a client reads an assessment
- **THEN** the boundary statement is present
