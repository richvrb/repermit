# Spec Delta

## Purpose

Makes documents the proof behind facts.

## ADDED Requirements

### Requirement: Facts are requested as documents
On a pack with document types, the system SHALL request open facts as documents and SHALL accept direct answers only for opening facts.

#### Scenario: Direct answer
- **WHEN** a response answers a fact that is not an opening fact
- **THEN** it is rejected

#### Scenario: Statement in text
- **WHEN** an applicant answers an AI question with text only
- **THEN** no fact is established

### Requirement: Real document upload
The system SHALL accept documents only as readable PDF files of an expected type.

#### Scenario: Invalid file
- **WHEN** a file is not a PDF
- **THEN** it is rejected and nothing is recorded

#### Scenario: Unknown type
- **WHEN** a document type is not defined in the pack
- **THEN** it is rejected

### Requirement: Document content is assessed
The system SHALL check each uploaded document against the checklist of its type in the next review.

#### Scenario: Awaiting assessment
- **WHEN** a document has been uploaded but not reviewed
- **THEN** a `document_pending` deficiency holds the case

#### Scenario: Item missing
- **WHEN** a checklist item is not reported as present
- **THEN** a `document_incomplete` deficiency names the item

#### Scenario: Wrong document
- **WHEN** a document is not the expected type or does not match the case
- **THEN** it counts as incomplete

#### Scenario: Complete
- **WHEN** all items are present
- **THEN** the requirement for that document is met

#### Scenario: New version
- **WHEN** a corrected document is uploaded
- **THEN** it is assessed again

### Requirement: Reviewer confirms facts
The system SHALL use a fact read from a document only after a resolution role has confirmed it.

#### Scenario: Awaiting confirmation
- **WHEN** a complete document states a needed fact
- **THEN** a `fact_to_confirm` deficiency shows the value and the quote

#### Scenario: Confirmed
- **WHEN** a reviewer confirms the fact
- **THEN** it is recorded as evidence and the rules use it

#### Scenario: Declined
- **WHEN** a reviewer declines the fact
- **THEN** it stays unknown and is requested again

#### Scenario: Unauthorized role
- **WHEN** another role tries to confirm a fact
- **THEN** the request is refused and recorded

#### Scenario: Fact outside the document's scope
- **WHEN** a review reads a fact the document type cannot prove
- **THEN** the fact is ignored

### Requirement: Synthetic documents
The system SHALL provide a sample PDF per requested document type for each AI test case, and an incomplete version.

#### Scenario: Sample
- **WHEN** a client requests a sample document
- **THEN** a readable PDF is returned
