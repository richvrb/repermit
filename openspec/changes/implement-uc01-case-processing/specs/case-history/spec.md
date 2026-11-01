# Spec Delta

## Purpose

Retains every input, decision, authorization outcome and state transition of a case, so that any conclusion can be reconstructed later.

## ADDED Requirements

### Requirement: Append-only history
The system SHALL record every change as an immutable, sequentially numbered event, and SHALL derive the current case state from those events.

#### Scenario: Ordered history
- **WHEN** a client requests a case history
- **THEN** all events are returned in sequence with type, timestamp and content

#### Scenario: State survives a restart
- **WHEN** the service restarts with the same database
- **THEN** a case reads back in the same state

### Requirement: Assessments are retained
The system SHALL retain each assessment with the revision and evidence versions it was based on, and SHALL expose only the latest assessment as current.

#### Scenario: Stale conclusion not used
- **WHEN** a later assessment replaces an earlier one
- **THEN** the case shows the later assessment and the earlier one remains in the history

### Requirement: Concurrent changes do not interleave
The system SHALL reject a write based on an outdated view of the case rather than merge it silently.

#### Scenario: Concurrent write
- **WHEN** two writes target the same event sequence number
- **THEN** one succeeds and the other returns a conflict error with no events written
