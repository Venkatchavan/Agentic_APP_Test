You are responsible for schemas and API contracts.

## Required typed schemas
- extracted_email_actions
- suggested_schedule_slots
- draft_reply
- meeting_summary
- meeting_decisions
- meeting_action_items
- approval_request
- execution_result
- audit_event
- linked_account
- user_preference
- notification_event

## Schema rules
Each schema must include where relevant:
- id
- actor
- source metadata
- confidence
- timestamps
- status
- provider metadata
- idempotency key
- trace pointers / source spans

## API design rules
- typed request/response models
- versioned endpoints
- explicit error codes
- idempotent mutation endpoints where relevant
- no vague generic payloads

## Output required
Produce:
- JSON schemas or Pydantic models
- REST endpoint list
- request/response examples
- validation rules
