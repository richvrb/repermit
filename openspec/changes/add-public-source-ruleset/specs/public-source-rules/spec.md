# Spec Delta

## Purpose

Bases assessments on rules derived from public Dubai sources, while keeping their provenance visible and their gaps explicit rather than filled in.

## ADDED Requirements

### Requirement: Non-synthetic rules are fully referenced
The system SHALL refuse to load a pack in which a rule from a non-synthetic source lacks a title, text or section reference, or in which such a source lacks an issuer and URL.

#### Scenario: Rule without a reference
- **WHEN** a pack contains a derived rule without a section reference
- **THEN** loading fails

### Requirement: Derived rules are labelled
Rules paraphrased or interpreted from public sources SHALL have source kind `derived`, and applied rules SHALL show their title, section reference and source title.

#### Scenario: Applied rule
- **WHEN** a derived rule is applied
- **THEN** the assessment shows source kind `derived` with its title, reference and source title

### Requirement: Dubai Building Code change types
The public pack SHALL classify modifications as `renovation`, `modification`, `reconstruction`, `change_of_use` or `addition`, with definitions following Dubai Building Code Table A.1.

#### Scenario: Covered change type
- **WHEN** a change is classified as `change_of_use`
- **THEN** the rules for that change type apply

#### Scenario: Uncovered change type
- **WHEN** a change type is outside these five
- **THEN** the case is `escalated` with a `retrieval_gap` issue

### Requirement: Rule conditions accept alternatives
A rule condition SHALL match when a fact equals its expected value or is one of a listed set of values.

#### Scenario: Listed value
- **WHEN** a rule lists several change types and the case has one of them
- **THEN** the condition matches

### Requirement: Facts are asked one at a time per rule
For a rule with unknown facts, the system SHALL report only the first unknown fact, with the question and answer options from the pack.

#### Scenario: Follow-up question
- **WHEN** a rule depends on two unknown facts
- **THEN** only the first is reported, and the second follows after the first is answered and matches

#### Scenario: Question from the pack
- **WHEN** an unknown fact has a question in the pack
- **THEN** the deficiency carries that question and its options

### Requirement: Unreachable requirements are gaps
Where the sources establish that a requirement exists but its content was not available, the pack SHALL declare a process gap and SHALL NOT state a value.

#### Scenario: Dubai Municipality document list
- **WHEN** a case falls under Dubai Municipality
- **THEN** the case is `escalated` with a `process_gap` issue that says the official document list was not available

#### Scenario: No fire values
- **WHEN** a fire compartment boundary is affected
- **THEN** a Civil Defence NOC is required and no fire rating value is stated

### Requirement: Each case keeps its pack
The system SHALL record the pack version when a case opens and SHALL use that pack for the whole case. Cases without a recorded pack SHALL use the synthetic pack.

#### Scenario: Fixed test case
- **WHEN** a fixed test case starts
- **THEN** it uses the synthetic pack, while a live case uses the public pack

#### Scenario: Earlier case
- **WHEN** a case opened before this change is read
- **THEN** it is assessed with the synthetic pack

### Requirement: LLM receives the rule content
The LLM prompt SHALL include rule text, section references, source titles, change type definitions and fact names from the case's pack.

#### Scenario: Prompt content
- **WHEN** a review is requested on a public pack case
- **THEN** the prompt contains the change type definitions, rule text and fact names
