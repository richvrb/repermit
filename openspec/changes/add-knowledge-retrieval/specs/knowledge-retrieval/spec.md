# Spec Delta

## Purpose

Gives LLM reviews traceable source passages.

## ADDED Requirements

### Requirement: Source register
Every indexed source SHALL be registered with issuer, date, url, language, jurisdiction and an enabled switch.

#### Scenario: Source disabled
- **WHEN** a source is disabled
- **THEN** its passages are not retrieved, without rebuilding the index

### Requirement: Jurisdiction filter
The system SHALL retrieve only passages that apply to the case's competent authority.

#### Scenario: Other authority
- **WHEN** a case falls under Dubai Municipality
- **THEN** passages for DDA are not retrieved

#### Scenario: Authority unknown
- **WHEN** the competent authority is not established
- **THEN** only passages for all authorities are retrieved

### Requirement: Superseded text
The system SHALL NOT retrieve articles marked as superseded.

#### Scenario: Replaced article
- **WHEN** an article has been replaced
- **THEN** it is left out of the results

### Requirement: Reviews use sources
The system SHALL pass retrieved passages to each LLM review, as data, and record which were provided.

#### Scenario: Review
- **WHEN** a review runs
- **THEN** the event lists the provided sources with reference and link

#### Scenario: No index
- **WHEN** no index is configured
- **THEN** the review runs without passages

### Requirement: Checked citations
The system SHALL keep only citations of passages that were provided.

#### Scenario: Unknown citation
- **WHEN** a review cites a passage that was not provided
- **THEN** the citation is removed and recorded as invalid

### Requirement: Sources advise only
Retrieved text SHALL NOT establish a fact or change a domain status.

#### Scenario: Passage about a domain
- **WHEN** a passage concerns a domain
- **THEN** the rule-based domain status is unchanged

### Requirement: Full text stays local
Full source texts SHALL stay out of git and the container image.

#### Scenario: Index location
- **WHEN** the index is built
- **THEN** it is written to the ignored `knowledge/` folder and mounted read-only
