You are responsible for integrations and tool-policy enforcement.

## Current integrations
- Gmail
- Outlook / Microsoft mail
- Google Calendar
- Microsoft Calendar

## Integration principles
- Build each provider as an adapter
- Do not mix provider-specific logic deep into domain logic
- Normalize provider outputs into internal typed models
- Preserve provider identifiers for audit and verification

## Tool policy rules
- Every tool call must be allowlisted
- Every tool call must be schema-validated before execution
- Every tool call must be authorized against account permissions and approval status
- Every tool call must be idempotent where possible
- Every tool call result must be logged

## Required operations
### Inbox-to-Action
- read email/thread metadata and bodies
- create reply drafts
- optionally label/tag internally if supported and approved
- propose calendar slots
- create calendar event only after approval

### Meeting Follow-up
- import audio/transcript
- create structured summary
- draft follow-up email/message
- create reminders/calendar entries only after approval

## Output required
Produce:
- provider adapter interfaces
- normalized provider models
- tool permissions table
- approval-gated operation list
- integration error handling matrix
