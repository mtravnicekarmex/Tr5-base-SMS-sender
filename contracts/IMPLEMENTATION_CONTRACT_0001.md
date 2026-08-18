# IMPLEMENTATION_CONTRACT_0001

Status: ARCHITECTURE_CHANGES_REQUESTED

---

# Workflow

- Created by: `architect`
- Reviewer (both review gates): `reviewer`
- Implementer: `programmer`
- Risk level: `standard`
- Currently with: `architect`
- Handed off to: `architect`
- Created at: `2026-08-18T11:25:10+02:00`
- Updated at: `2026-08-18T11:27:08+02:00`

---

# Title

Rewrite source/project/README.md to reflect actual current project state

---

# Purpose

source/project/README.md still shows the generic Tr5-base placeholder text ("Directory exists. No project code yet"), even though source/project already holds a working CLI and Streamlit tool for managing GSM gate phone number lists. This mismatch was flagged during the architect's code review of source/project as a documentation-debt item (P6: Current State must reflect facts) and the owner asked for it to be handled as its own contract rather than the light path. Fixing it gives anyone opening the project directory an accurate first read of what actually exists there, instead of text that contradicts the repository.

---

# Intent

This change only rewrites the content of source/project/README.md so its Purpose / Current capabilities / Current limitations / Planned evolution sections match what is actually in source/project today. It deliberately documents known gaps (e.g. missing CLI/UI test coverage, no concurrent-write protection on the shared Excel workbook, CLI/UI parameter parity, the single global phone-column-index assumption) as limitations to read, not as work to perform now — those are separate, already-queued follow-up topics from the same code review. No other file in the repository is touched, and no behavior, public API, or structure of the application itself changes.

---

# Current State

source/project/README.md currently contains the original Tr5-base 'point zero' placeholder: a Purpose section describing an empty project directory, a 'Current capabilities (v0.1)' section stating 'Directory exists. No project code yet', a 'Current limitations' section stating 'Empty until the first contract is implemented', and a 'Planned evolution' section referencing PRINCIPLES.md P1/P15. In reality, source/project already contains: send_sms.py (core logic — TOML config loading, phone number normalization/validation, sheet analysis for duplicates/invalid rows, SmsGatewayClient, safe in-place Excel writes via temp file + atomic replace with optional timestamped backup), main.py (CLI with six subcommands: send, send-batch, supplement, find-one, find-sheet, duplicates, each with --dry-run support where applicable), streamlit_app.py (web UI: sheet overview, inline sheet editor with save-back-to-Excel, ADD/FIND batch operations, one-off SMS, data quality/duplicate checks), tests/test_send_sms.py (8 unit tests covering the core logic), and config.example.toml (configuration template; the real config.toml is gitignored). No other file under source/project is affected by this contract.

---

# Inputs

The existing (stale) content of source/project/README.md; the actual current contents of source/project/main.py, source/project/streamlit_app.py, source/project/send_sms.py, source/project/tests/test_send_sms.py, and source/project/config.example.toml as the factual basis for the rewrite; the wording convention already used in the existing 'Planned evolution' section (reference to PRINCIPLES.md P1, P15).

---

# Outputs

An updated source/project/README.md with four sections — Purpose, Current capabilities (v0.1), Current limitations, Planned evolution — whose content accurately reflects the current repository state described above. No other file is created or modified.

---

# Functional Requirements

## Point 1

SHALL: Replace the 'Purpose' section of source/project/README.md so it states that this directory holds the actual application code for the SMS gateway helper project (a CLI and Streamlit tool for managing GSM gate phone number lists over an SMS gateway), kept separate from the agentic framework/governance layer at the repository root, with contract changes landing here — removing all wording implying the directory is empty or unstarted.

Acceptance criteria:
- source/project/README.md contains a 'Purpose' (or '## Purpose') section that no longer contains the phrase 'No project code yet' or equivalent 'empty/unstarted' wording
- The Purpose section explicitly names the project as a tool for managing GSM gate phone numbers via an SMS gateway
- The Purpose section still states that this directory is kept separate from the framework/governance layer at the repository root

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 2

SHALL: Replace the 'Current capabilities (v0.1)' section of source/project/README.md with an accurate list of what exists today: send_sms.py (core logic: config loading, phone number normalization/validation, sheet analysis, SMS gateway client, safe Excel writes with optional backup), main.py (CLI with its six subcommands: send, send-batch, supplement, find-one, find-sheet, duplicates), streamlit_app.py (web UI: sheet overview, inline editor with save-to-Excel, ADD/FIND batch operations, one-off SMS, data quality checks), tests/test_send_sms.py (unit tests for the core logic), and config.example.toml (configuration template).

Acceptance criteria:
- The 'Current capabilities (v0.1)' section lists send_sms.py, main.py, streamlit_app.py, tests/test_send_sms.py, and config.example.toml by filename with an accurate one-line description of each, matching their actual contents
- The section names all six main.py subcommands (send, send-batch, supplement, find-one, find-sheet, duplicates)
- The section no longer contains the phrase 'Directory exists. No project code yet' or any equivalent placeholder statement

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 3

SHALL: Replace the 'Current limitations' section of source/project/README.md with the following documented gaps: no automated tests for main.py (CLI argument parsing / exit codes) or for streamlit_app.py; no file locking for concurrent writes to the shared Excel workbook when multiple users save through the Streamlit editor at the same time; CLI commands do not expose a --timeout option unlike the Streamlit UI; the phone number column layout is assumed uniform across all configured gate sheets via a single global column-index constant.

Acceptance criteria:
- The 'Current limitations' section lists all four items above, each as a distinct bullet or sentence
- The section no longer contains the phrase 'Empty until the first contract is implemented against a real project' or any equivalent placeholder statement
- None of the four listed limitations is described as fixed or resolved in this same document (only documented as a current gap)

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 4

SHALL: Update the 'Planned evolution' section of source/project/README.md so it states that the project grows as further contracts are implemented and that resolving the limitations listed above (concurrent-write protection, CLI/UI parameter parity, per-gate column configuration, additional test coverage) is deferred to those future contracts, while keeping the existing reference to PRINCIPLES.md P1 and P15 on deciding structure only when actually needed.

Acceptance criteria:
- The 'Planned evolution' section references PRINCIPLES.md P1 and P15
- The section explicitly states that the limitations listed in 'Current limitations' are deferred to future contracts rather than addressed here
- The section does not commit to a specific implementation timeline or design for any deferred item

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 5

SHALL: Verify that source/project/README.md is internally consistent after the rewrite and that no other file in the repository was modified as part of this change.

Acceptance criteria:
- A full read-through of source/project/README.md shows no remaining contradictions between its four sections (e.g. no section still implying the directory is empty)
- `git status` (or equivalent diff check) shows source/project/README.md as the only changed file
- No stale placeholder phrases from the original Tr5-base template ('point zero', 'No project code yet', 'Empty until the first contract is implemented') remain anywhere in the file

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

---

# Out of Scope

This contract SHALL NOT modify any file other than source/project/README.md (main.py, streamlit_app.py, send_sms.py, tests/test_send_sms.py, config.example.toml, .gitignore, pyproject.toml, SESSION_2026-04-10.md must remain unchanged). It SHALL NOT implement, fix, or otherwise act on any of the limitations documented in the README (no file locking, no CLI --timeout flags, no new tests, no per-gate column configuration) — those are documented as known limitations only. It SHALL NOT add features, sections, or claims beyond the four-section structure agreed with the owner. It SHALL NOT write a memory/CHANGE_LOG.md entry (that mechanism applies to light-path fixes only; this change is tracked through the contract itself).

---

# Acceptance Criteria

Acceptance criteria are listed per point in the Functional Requirements section.

---

# Architecture Review

### Round 1 — 2026-08-18T11:27:08+02:00 — Verdict: CHANGES_REQUESTED — Reviewer: `reviewer`

Checked the contract's factual claims about source/project against the actual files (main.py's six subparsers — send, send-batch, supplement, find-one, find-sheet, duplicates — verified via grep; tests/test_send_sms.py's 8 test methods verified by name; config.toml gitignored via source/project/.gitignore verified). Those facts are accurate, so P6 ('Current State contains facts') is satisfied at the content level.

However, the contract's target path is architecturally wrong. `AGENTS.md` states explicitly: '`source/` holds the original/input source code of an existing project being migrated onto this pipeline — read-only reference, never edited directly; migrated/new code lands in `project/` instead — see ADR-024.' ADR-024 in memory/DECISIONS.md confirms the same: source/ is 'copied in as-is and kept untouched'; migrated/rewritten code lands in `project/` contract by contract. `memory/CURRENT_STATE.md` (the Discovery Engine's own generated inventory) confirms `source/project/` is a full nested copy of a prior bod-nula-based project (including its own `.git`, its own `agents/`, `memory/`, `contracts/`, and its own `project/` subdirectory holding the real SMS app) — exactly the 'original/input source being migrated' that ADR-024 describes, not a place where documentation is meant to be actively maintained going forward.

All five points of this contract, and its Outputs/Out-of-Scope sections, are built entirely around rewriting `source/project/README.md` — a file inside that read-only reference tree. This directly contradicts the explicit 'never edited directly' rule. The top-level `project/README.md` (which already exists, still holding the generic point-zero placeholder, and is exactly the file ADR-015/ADR-016 designate for describing 'the actual application code being built through the contract pipeline') was not touched or even considered by this contract — meaning the underlying documentation-debt problem (P6) is real, but the fix as scoped will leave the actually-governed, non-read-only README (`project/README.md`) still wrong while illegitimately editing a file that policy says must stay untouched. This is not a matter of style; it is the premise of the whole contract, so it cannot be salvaged by tweaking a single point's wording.

Other checks: points are individually specific and independently verifiable (acceptance criteria reference concrete phrases to remove/add), no naming-convention violation (README.md), no destructive commands or access beyond `edit`, no backward-compatibility concern (docs-only), and risk_level `standard` is correctly assessed (no credentials, no external calls, no native/hardware libraries, no personal/real data — config.toml stays gitignored). These are not blocking issues; only the target-path violation is.

Recommendation for revision: either retarget every point at `project/README.md` (documenting current_state honestly, i.e. that the real SMS/Streamlit code has not yet been migrated there and still lives only in the read-only `source/project/` reference — which is a materially different and smaller truth than what this draft currently proposes to write), or scope this as part of an actual migration contract that moves the code from `source/project/` into `project/` per ADR-024's intended flow. Either path requires the architect to rewrite the contract, not the programmer to interpret around a target it cannot legally write to.

---

# Future Evolution

The limitations this README will document (concurrent-write protection for the shared Excel workbook, CLI/Streamlit UI parameter parity such as --timeout, per-gate phone-column-layout configuration, test coverage for main.py and streamlit_app.py) are candidates for separate future contracts already identified in the architect's code review queue. This contract only records them as limitations; resolving any of them is deliberately deferred to those later contracts.

---

# Completion Notes

_Awaiting implementation._

---

# Implementation Review

_Awaiting implementation review._

---

# Lessons Learned

_Not filled in._

---

<!-- CONTRACT-META
{
  "number": 1,
  "title": "Rewrite source/project/README.md to reflect actual current project state",
  "status": "ARCHITECTURE_CHANGES_REQUESTED",
  "created_by": "architect",
  "assigned_to": "architect",
  "handoff_to": "architect",
  "created_at": "2026-08-18T11:25:10+02:00",
  "updated_at": "2026-08-18T11:27:08+02:00",
  "points": [
    {
      "number": 1,
      "assignment": "Replace the 'Purpose' section of source/project/README.md so it states that this directory holds the actual application code for the SMS gateway helper project (a CLI and Streamlit tool for managing GSM gate phone number lists over an SMS gateway), kept separate from the agentic framework/governance layer at the repository root, with contract changes landing here — removing all wording implying the directory is empty or unstarted.",
      "acceptance_criteria": [
        "source/project/README.md contains a 'Purpose' (or '## Purpose') section that no longer contains the phrase 'No project code yet' or equivalent 'empty/unstarted' wording",
        "The Purpose section explicitly names the project as a tool for managing GSM gate phone numbers via an SMS gateway",
        "The Purpose section still states that this directory is kept separate from the framework/governance layer at the repository root"
      ],
      "programmer_note": "",
      "programmer_note_author": "",
      "programmer_note_at": "",
      "programmer_files": [],
      "programmer_tests": [],
      "reviewer_note": "",
      "reviewer_note_author": "",
      "reviewer_note_at": "",
      "status": "PENDING"
    },
    {
      "number": 2,
      "assignment": "Replace the 'Current capabilities (v0.1)' section of source/project/README.md with an accurate list of what exists today: send_sms.py (core logic: config loading, phone number normalization/validation, sheet analysis, SMS gateway client, safe Excel writes with optional backup), main.py (CLI with its six subcommands: send, send-batch, supplement, find-one, find-sheet, duplicates), streamlit_app.py (web UI: sheet overview, inline editor with save-to-Excel, ADD/FIND batch operations, one-off SMS, data quality checks), tests/test_send_sms.py (unit tests for the core logic), and config.example.toml (configuration template).",
      "acceptance_criteria": [
        "The 'Current capabilities (v0.1)' section lists send_sms.py, main.py, streamlit_app.py, tests/test_send_sms.py, and config.example.toml by filename with an accurate one-line description of each, matching their actual contents",
        "The section names all six main.py subcommands (send, send-batch, supplement, find-one, find-sheet, duplicates)",
        "The section no longer contains the phrase 'Directory exists. No project code yet' or any equivalent placeholder statement"
      ],
      "programmer_note": "",
      "programmer_note_author": "",
      "programmer_note_at": "",
      "programmer_files": [],
      "programmer_tests": [],
      "reviewer_note": "",
      "reviewer_note_author": "",
      "reviewer_note_at": "",
      "status": "PENDING"
    },
    {
      "number": 3,
      "assignment": "Replace the 'Current limitations' section of source/project/README.md with the following documented gaps: no automated tests for main.py (CLI argument parsing / exit codes) or for streamlit_app.py; no file locking for concurrent writes to the shared Excel workbook when multiple users save through the Streamlit editor at the same time; CLI commands do not expose a --timeout option unlike the Streamlit UI; the phone number column layout is assumed uniform across all configured gate sheets via a single global column-index constant.",
      "acceptance_criteria": [
        "The 'Current limitations' section lists all four items above, each as a distinct bullet or sentence",
        "The section no longer contains the phrase 'Empty until the first contract is implemented against a real project' or any equivalent placeholder statement",
        "None of the four listed limitations is described as fixed or resolved in this same document (only documented as a current gap)"
      ],
      "programmer_note": "",
      "programmer_note_author": "",
      "programmer_note_at": "",
      "programmer_files": [],
      "programmer_tests": [],
      "reviewer_note": "",
      "reviewer_note_author": "",
      "reviewer_note_at": "",
      "status": "PENDING"
    },
    {
      "number": 4,
      "assignment": "Update the 'Planned evolution' section of source/project/README.md so it states that the project grows as further contracts are implemented and that resolving the limitations listed above (concurrent-write protection, CLI/UI parameter parity, per-gate column configuration, additional test coverage) is deferred to those future contracts, while keeping the existing reference to PRINCIPLES.md P1 and P15 on deciding structure only when actually needed.",
      "acceptance_criteria": [
        "The 'Planned evolution' section references PRINCIPLES.md P1 and P15",
        "The section explicitly states that the limitations listed in 'Current limitations' are deferred to future contracts rather than addressed here",
        "The section does not commit to a specific implementation timeline or design for any deferred item"
      ],
      "programmer_note": "",
      "programmer_note_author": "",
      "programmer_note_at": "",
      "programmer_files": [],
      "programmer_tests": [],
      "reviewer_note": "",
      "reviewer_note_author": "",
      "reviewer_note_at": "",
      "status": "PENDING"
    },
    {
      "number": 5,
      "assignment": "Verify that source/project/README.md is internally consistent after the rewrite and that no other file in the repository was modified as part of this change.",
      "acceptance_criteria": [
        "A full read-through of source/project/README.md shows no remaining contradictions between its four sections (e.g. no section still implying the directory is empty)",
        "`git status` (or equivalent diff check) shows source/project/README.md as the only changed file",
        "No stale placeholder phrases from the original Tr5-base template ('point zero', 'No project code yet', 'Empty until the first contract is implemented') remain anywhere in the file"
      ],
      "programmer_note": "",
      "programmer_note_author": "",
      "programmer_note_at": "",
      "programmer_files": [],
      "programmer_tests": [],
      "reviewer_note": "",
      "reviewer_note_author": "",
      "reviewer_note_at": "",
      "status": "PENDING"
    }
  ],
  "implementer": "programmer",
  "reviewer": "reviewer",
  "risk_level": "standard",
  "purpose": "source/project/README.md still shows the generic Tr5-base placeholder text (\"Directory exists. No project code yet\"), even though source/project already holds a working CLI and Streamlit tool for managing GSM gate phone number lists. This mismatch was flagged during the architect's code review of source/project as a documentation-debt item (P6: Current State must reflect facts) and the owner asked for it to be handled as its own contract rather than the light path. Fixing it gives anyone opening the project directory an accurate first read of what actually exists there, instead of text that contradicts the repository.",
  "intent": "This change only rewrites the content of source/project/README.md so its Purpose / Current capabilities / Current limitations / Planned evolution sections match what is actually in source/project today. It deliberately documents known gaps (e.g. missing CLI/UI test coverage, no concurrent-write protection on the shared Excel workbook, CLI/UI parameter parity, the single global phone-column-index assumption) as limitations to read, not as work to perform now — those are separate, already-queued follow-up topics from the same code review. No other file in the repository is touched, and no behavior, public API, or structure of the application itself changes.",
  "current_state": "source/project/README.md currently contains the original Tr5-base 'point zero' placeholder: a Purpose section describing an empty project directory, a 'Current capabilities (v0.1)' section stating 'Directory exists. No project code yet', a 'Current limitations' section stating 'Empty until the first contract is implemented', and a 'Planned evolution' section referencing PRINCIPLES.md P1/P15. In reality, source/project already contains: send_sms.py (core logic — TOML config loading, phone number normalization/validation, sheet analysis for duplicates/invalid rows, SmsGatewayClient, safe in-place Excel writes via temp file + atomic replace with optional timestamped backup), main.py (CLI with six subcommands: send, send-batch, supplement, find-one, find-sheet, duplicates, each with --dry-run support where applicable), streamlit_app.py (web UI: sheet overview, inline sheet editor with save-back-to-Excel, ADD/FIND batch operations, one-off SMS, data quality/duplicate checks), tests/test_send_sms.py (8 unit tests covering the core logic), and config.example.toml (configuration template; the real config.toml is gitignored). No other file under source/project is affected by this contract.",
  "inputs": "The existing (stale) content of source/project/README.md; the actual current contents of source/project/main.py, source/project/streamlit_app.py, source/project/send_sms.py, source/project/tests/test_send_sms.py, and source/project/config.example.toml as the factual basis for the rewrite; the wording convention already used in the existing 'Planned evolution' section (reference to PRINCIPLES.md P1, P15).",
  "outputs": "An updated source/project/README.md with four sections — Purpose, Current capabilities (v0.1), Current limitations, Planned evolution — whose content accurately reflects the current repository state described above. No other file is created or modified.",
  "out_of_scope": "This contract SHALL NOT modify any file other than source/project/README.md (main.py, streamlit_app.py, send_sms.py, tests/test_send_sms.py, config.example.toml, .gitignore, pyproject.toml, SESSION_2026-04-10.md must remain unchanged). It SHALL NOT implement, fix, or otherwise act on any of the limitations documented in the README (no file locking, no CLI --timeout flags, no new tests, no per-gate column configuration) — those are documented as known limitations only. It SHALL NOT add features, sections, or claims beyond the four-section structure agreed with the owner. It SHALL NOT write a memory/CHANGE_LOG.md entry (that mechanism applies to light-path fixes only; this change is tracked through the contract itself).",
  "future_evolution": "The limitations this README will document (concurrent-write protection for the shared Excel workbook, CLI/Streamlit UI parameter parity such as --timeout, per-gate phone-column-layout configuration, test coverage for main.py and streamlit_app.py) are candidates for separate future contracts already identified in the architect's code review queue. This contract only records them as limitations; resolving any of them is deliberately deferred to those later contracts.",
  "lessons_learned": "",
  "architecture_review_rounds": [
    {
      "round": 1,
      "date": "2026-08-18T11:27:08+02:00",
      "verdict": "CHANGES_REQUESTED",
      "reviewer": "reviewer",
      "findings": "Checked the contract's factual claims about source/project against the actual files (main.py's six subparsers — send, send-batch, supplement, find-one, find-sheet, duplicates — verified via grep; tests/test_send_sms.py's 8 test methods verified by name; config.toml gitignored via source/project/.gitignore verified). Those facts are accurate, so P6 ('Current State contains facts') is satisfied at the content level.\n\nHowever, the contract's target path is architecturally wrong. `AGENTS.md` states explicitly: '`source/` holds the original/input source code of an existing project being migrated onto this pipeline — read-only reference, never edited directly; migrated/new code lands in `project/` instead — see ADR-024.' ADR-024 in memory/DECISIONS.md confirms the same: source/ is 'copied in as-is and kept untouched'; migrated/rewritten code lands in `project/` contract by contract. `memory/CURRENT_STATE.md` (the Discovery Engine's own generated inventory) confirms `source/project/` is a full nested copy of a prior bod-nula-based project (including its own `.git`, its own `agents/`, `memory/`, `contracts/`, and its own `project/` subdirectory holding the real SMS app) — exactly the 'original/input source being migrated' that ADR-024 describes, not a place where documentation is meant to be actively maintained going forward.\n\nAll five points of this contract, and its Outputs/Out-of-Scope sections, are built entirely around rewriting `source/project/README.md` — a file inside that read-only reference tree. This directly contradicts the explicit 'never edited directly' rule. The top-level `project/README.md` (which already exists, still holding the generic point-zero placeholder, and is exactly the file ADR-015/ADR-016 designate for describing 'the actual application code being built through the contract pipeline') was not touched or even considered by this contract — meaning the underlying documentation-debt problem (P6) is real, but the fix as scoped will leave the actually-governed, non-read-only README (`project/README.md`) still wrong while illegitimately editing a file that policy says must stay untouched. This is not a matter of style; it is the premise of the whole contract, so it cannot be salvaged by tweaking a single point's wording.\n\nOther checks: points are individually specific and independently verifiable (acceptance criteria reference concrete phrases to remove/add), no naming-convention violation (README.md), no destructive commands or access beyond `edit`, no backward-compatibility concern (docs-only), and risk_level `standard` is correctly assessed (no credentials, no external calls, no native/hardware libraries, no personal/real data — config.toml stays gitignored). These are not blocking issues; only the target-path violation is.\n\nRecommendation for revision: either retarget every point at `project/README.md` (documenting current_state honestly, i.e. that the real SMS/Streamlit code has not yet been migrated there and still lives only in the read-only `source/project/` reference — which is a materially different and smaller truth than what this draft currently proposes to write), or scope this as part of an actual migration contract that moves the code from `source/project/` into `project/` per ADR-024's intended flow. Either path requires the architect to rewrite the contract, not the programmer to interpret around a target it cannot legally write to."
    }
  ],
  "completion_notes": "",
  "implementation_review_rounds": []
}
CONTRACT-META -->
