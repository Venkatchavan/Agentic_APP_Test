# Agentic App

Multi-platform productivity app with two AI-powered agentic workflows:
1. **Inbox-to-Action** — AI extracts actions from emails, drafts replies, proposes calendar events
2. **Meeting Follow-up** — AI summarizes transcripts, extracts decisions & action items, drafts follow-ups

All AI-generated outputs go through a **human-in-the-loop approval gate** before any external side effects.

## Architecture

```
├── backend/          # FastAPI + SQLAlchemy + Celery
│   ├── app/
│   │   ├── auth/         # JWT authentication
│   │   ├── accounts/     # Linked OAuth accounts
│   │   ├── providers/    # Gmail, Outlook, Calendar adapters
│   │   ├── inbox/        # Email ingestion & AI extraction
│   │   ├── meetings/     # Transcript import & AI summarization
│   │   ├── drafts/       # AI-generated draft replies
│   │   ├── scheduling/   # Calendar slot proposals
│   │   ├── approvals/    # Central approval gate
│   │   ├── execution/    # Approved action dispatcher
│   │   ├── audit/        # Immutable event log
│   │   ├── notifications/# User notifications
│   │   ├── ai/           # Model-agnostic AI client
│   │   └── workers/      # Celery background tasks
│   └── alembic/          # DB migrations
├── mobile/           # Flutter cross-platform app
│   └── lib/
│       ├── core/         # Theme, routing, auth, networking
│       ├── models/       # Data models
│       ├── services/     # API service layer
│       ├── features/     # Feature screens
│       └── shared/       # Reusable widgets
├── prompt-system/    # Prompt engineering pack
└── docker-compose.yml
```

## Quick Start

```bash
# 1. Start infrastructure
docker-compose up -d postgres redis

# 2. Backend
cd backend
cp .env.example .env  # fill in secrets
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# 3. Mobile
cd mobile
flutter pub get
flutter run
```

## Key Design Principles

- **Approval-gated execution** — No auto-send, no auto-create. Every external action requires explicit human approval.
- **Provider adapter pattern** — Abstract interfaces for email/calendar with concrete Gmail, Outlook, Google Calendar, Microsoft Calendar implementations.
- **Deterministic AI validation** — All AI outputs are validated with regex/JSON schema checks before storage.
- **Sub-300-line files** — Every code file is under 300 lines for readability and maintainability.
- **Audit trail** — Every significant action is logged in an append-only audit table.
