# Agentic Inbox & Meeting Follow-up App — Prompt System

## Overview
This is the **prompt repository** for a production-grade, multi-platform mobile app (iOS + Android, phones + tablets) with two agentic workflows:

1. **Inbox-to-Action Agent** — connects Gmail/Outlook, extracts tasks, drafts replies, proposes schedule slots, requires human approval before any external action.
2. **Meeting Follow-up Agent** — imports audio/transcripts, generates summaries, extracts decisions/tasks/owners, drafts follow-ups, requires human approval before any external action.

## Repository Structure

```text
prompt-system/
├── README.md                          # this file
├── VERSIONING.md                      # versioning policy
├── CHANGELOG.md                       # change history
├── prompt-manifest.yaml               # manifest of all prompts and execution order
├── prompts/
│   ├── 00_master_orchestrator.md      # principal orchestrator prompt
│   ├── 01_product_scope_and_prd.md    # PRD and product scope
│   ├── 02_mobile_platform_rules.md    # Flutter / mobile platform rules
│   ├── 03_security_privacy_and_compliance.md  # security, privacy, compliance
│   ├── 04_agentic_runtime_rules.md    # runtime agent policies
│   ├── 05_integrations_and_tool_policies.md   # integration adapters & tool policy
│   ├── 06_backend_architecture.md     # backend architecture
│   ├── 07_data_models_and_contracts.md        # schemas & API contracts
│   ├── 08_ui_ux_rules.md             # UX and trust-layer design
│   ├── 09_evaluation_and_test_harness.md      # evaluation & testing
│   ├── 10_documentation_update_rules.md       # docs enforcement
│   ├── 11_release_and_version_control_rules.md # release & versioning
│   ├── 12_team_mode_and_admin_rules.md        # team-mode & RBAC
│   ├── 13_observability_and_cost_controls.md  # observability & AI cost governance
│   └── 14_phase_execution_template.md         # per-phase execution template
├── templates/
│   ├── prd_template.md
│   ├── architecture_decision_record.md
│   ├── threat_model_template.md
│   ├── api_contract_template.md
│   ├── changelog_template.md
│   ├── release_notes_template.md
│   └── evaluation_report_template.md
└── examples/
    ├── claude_code_bootstrap.md
    ├── crewai_system_prompt.md
    └── implementation_handoff.md
```

## How to Use

### Claude Code / Cursor Bootstrap Order
1. Load `00_master_orchestrator.md`
2. Load `01_product_scope_and_prd.md`
3. Load `02_mobile_platform_rules.md`
4. Load `03_security_privacy_and_compliance.md`
5. Load `04_agentic_runtime_rules.md`
6. Then load phase-specific prompt(s)
7. For each phase, also load `10_documentation_update_rules.md` and `11_release_and_version_control_rules.md`

### Rule
**Never run implementation without security rules + docs-update rules + version-control rules active.**

### CrewAI / LangGraph
See `examples/crewai_system_prompt.md` for a system prompt that references the hard-policy files.

## Owner
**Venkat Chavan N**

## License
Internal / proprietary prompt pack.
