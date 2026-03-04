# Claude Code / Cursor Bootstrap Guide

## Purpose
This guide shows how to load the prompt pack in Claude Code or Cursor for implementation work.

---

## Step 1: Load Core Prompts (always required)

Load these **in order** at the start of every session:

1. `prompts/00_master_orchestrator.md` — sets role, constraints, deliverables, and philosophy
2. `prompts/01_product_scope_and_prd.md` — defines users, features, MVP scope
3. `prompts/02_mobile_platform_rules.md` — Flutter, adaptive UI, background tasks
4. `prompts/03_security_privacy_and_compliance.md` — security/privacy hard rules
5. `prompts/04_agentic_runtime_rules.md` — runtime policy, approval state machine

---

## Step 2: Load Hard-Policy Prompts (always active during implementation)

These must remain active whenever code is being written or reviewed:

- `prompts/10_documentation_update_rules.md`
- `prompts/11_release_and_version_control_rules.md`

---

## Step 3: Load Phase-Specific Prompts

Based on your current implementation phase, load the relevant prompt(s):

| Phase | Prompts to load |
|-------|----------------|
| Backend design | `06_backend_architecture.md`, `07_data_models_and_contracts.md` |
| Integrations | `05_integrations_and_tool_policies.md` |
| UI/UX | `08_ui_ux_rules.md` |
| Testing | `09_evaluation_and_test_harness.md` |
| Team features | `12_team_mode_and_admin_rules.md` |
| Observability | `13_observability_and_cost_controls.md` |

---

## Step 4: Use the Phase Template

For each implementation phase, copy `prompts/14_phase_execution_template.md` and fill it out.

---

## Rule
**Never run implementation without security rules + docs-update rules + version-control rules active.**

---

## Example Claude Code Session

```
# Session start
Load: 00, 01, 02, 03, 04, 10, 11

# Phase 1: Backend scaffold
Also load: 06, 07
Fill out: 14_phase_execution_template.md for "Phase 1: Backend Scaffold"
Implement, then produce end-of-phase report.

# Phase 2: Provider adapters
Also load: 05
Fill out: 14_phase_execution_template.md for "Phase 2: Provider Adapters"
Implement, then produce end-of-phase report.

# Phase 3: Flutter app scaffold
Also load: 08
Fill out: 14_phase_execution_template.md for "Phase 3: Flutter App Scaffold"
...and so on.
```

---

## Tips
- Keep the manifest (`prompt-manifest.yaml`) up to date after any prompt changes
- Update `CHANGELOG.md` after every phase
- Reference ADR template when making non-trivial architecture decisions
- Use evaluation report template when running test/benchmark passes
