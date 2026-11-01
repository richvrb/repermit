# Spec Delta

## Purpose

Packages RePermit so it can be built, configured and run as containers with observable health.

## ADDED Requirements

### Requirement: Container image
The project SHALL build a container image that runs the service as a non-root user and contains the default knowledge pack.

#### Scenario: Image runs
- **WHEN** the image is built and started
- **THEN** the service answers on its configured port as a non-root user

### Requirement: Environment configuration
The service SHALL read its database URL and knowledge pack path from environment variables, defaulting to a local SQLite file and the bundled pack.

#### Scenario: Default configuration
- **WHEN** the service starts with no environment configuration
- **THEN** it uses SQLite and the bundled pack

### Requirement: Health endpoints
The service SHALL expose a liveness endpoint and a readiness endpoint, and readiness SHALL fail when the database is unreachable.

#### Scenario: Ready service
- **WHEN** the database is reachable
- **THEN** the readiness endpoint returns success with the pack version

#### Scenario: Database unavailable
- **WHEN** the database is unreachable
- **THEN** the readiness endpoint returns service-unavailable

### Requirement: Compose stack
The project SHALL provide a Compose stack running the service with PostgreSQL and persistent storage, publishing the service on the loopback interface only.

#### Scenario: Stack started
- **WHEN** the stack is started
- **THEN** the service becomes ready against PostgreSQL and is reachable on localhost
