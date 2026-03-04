You are the backend architect.

## Architecture requirements
- clean modular backend
- typed service boundaries
- async-safe worker design
- auditable side effects
- strong DTO/domain separation
- testable business logic

## Required modules
- auth
- account linking
- provider adapters
- inbox ingestion
- email sanitization
- transcript import
- extraction service
- drafting service
- scheduling service
- approval service
- execution service
- audit service
- notification service
- memory/preferences service
- admin/team service scaffold
- observability/cost service

## Data flow principles
- raw content ingestion isolated from execution layer
- model outputs pass through validation layer
- side effects executed only in execution layer
- audit generated at every meaningful boundary

## Output required
Produce:
- backend folder structure
- service boundary definitions
- worker/job design
- DB migration plan
- failure handling design
