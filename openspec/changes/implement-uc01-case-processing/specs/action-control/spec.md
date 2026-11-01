# Spec Delta

## Purpose

Decides the next permitted action, keeping the autonomy assessment separate from mandatory authorization so that nothing unsupported or unauthorized changes a case.

## ADDED Requirements

### Requirement: Plan the next action
The system SHALL propose the process action available from the current stage, and SHALL list it as held with reasons while deficiencies or open issues remain.

#### Scenario: Ready case
- **WHEN** an assessment has no deficiencies and no open issues
- **THEN** the plan names the next action and it is not held

#### Scenario: Held action
- **WHEN** an assessment has a deficiency
- **THEN** the plan marks the next action as held and states why

### Requirement: Evaluate autonomy
The system SHALL classify the next action as `autonomous`, `human_review` or `human_only`. A conditional action SHALL be `human_review` when a safety domain is affected.

#### Scenario: Safety domain affected
- **WHEN** a conditional action is planned and fire safety is affected
- **THEN** its autonomy is `human_review` and it is not executed automatically

#### Scenario: Autonomous action executed
- **WHEN** the next action is `autonomous`, not held, and the responsible role is authorized
- **THEN** the system executes it and the case moves to the next stage

### Requirement: Authorization is mandatory
The system SHALL deny any action whose actor role is not permitted, regardless of the autonomy classification, and SHALL record the denial.

#### Scenario: Unauthorized manual action
- **WHEN** an actor without the required role requests an action
- **THEN** the system returns a forbidden error, records the denial and leaves the stage unchanged

#### Scenario: Autonomy does not override authorization
- **WHEN** an autonomous action is ready but the responsible role lacks permission
- **THEN** execution is denied, the denial is recorded and the stage is unchanged

#### Scenario: Valid authorization obtained
- **WHEN** an actor with the required role requests the previously denied action
- **THEN** the action executes

### Requirement: Held actions do not change the case
The system SHALL refuse an action that is held or not available from the current stage, SHALL record the refusal, and SHALL leave the stage unchanged.

#### Scenario: Action requested while held
- **WHEN** an authorized actor requests an action while the case has a deficiency
- **THEN** the system returns a conflict error, records the refusal and leaves the stage unchanged

### Requirement: Simulated execution only
The system SHALL perform actions only as simulated stage changes and SHALL NOT contact any external system.

#### Scenario: Approval is simulated
- **WHEN** the authority role approves a modification
- **THEN** the case reaches stage `approved_simulated` and status `completed`
