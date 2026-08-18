# IMPLEMENTATION_CONTRACT_0001

Status: READY_FOR_PROGRAMMER

---

# Workflow

- Created by: `architect`
- Reviewer (both review gates): `reviewer`
- Implementer: `programmer`
- Risk level: `standard`
- Currently with: `programmer`
- Handed off to: `programmer`
- Created at: `2026-08-18T11:25:10+02:00`
- Updated at: `2026-08-18T14:46:58+02:00`

---

# Title

Rewrite project/README.md to reflect the actual, now-migrated project state

---

# Purpose

project/README.md still shows the generic Tr5-base placeholder text ("Directory exists. No project code yet"), even though project/ now holds a working, migrated, and manually-verified (8/8 tests passing) CLI and Streamlit tool for managing GSM gate phone number lists — moved there by IMPLEMENTATION_CONTRACT_0002 from the read-only source/project/ reference. This mismatch was originally flagged during the architect's code review as a documentation-debt item (P6: Current State must reflect facts); the first attempt at fixing it (this same contract's round 1) mistakenly targeted the read-only source/project/README.md, which architecture review correctly rejected per ADR-024 ('source/ stays untouched, never edited directly'). Now that the migration has landed and been verified, fixing project/README.md gives anyone opening the actual, governed project directory an accurate first read of what exists there, instead of text that contradicts the repository.

---

# Intent

This change only rewrites the content of project/README.md so its Purpose / Current capabilities / Current limitations / Planned evolution sections match what is actually in project/ today, post-migration. It documents known gaps (missing CLI/UI test coverage, no concurrent-write protection on the shared Excel workbook, CLI/UI parameter parity, the single global phone-column-index assumption) as limitations to read, not as work to perform now — those remain separate, already-queued follow-up contracts. It additionally documents, for the first time, the project-scoped project/.venv the owner created and populated manually (per IMPLEMENTATION_CONTRACT_0002's Out of Scope, since the programmer has no Bash access to do this itself), so future readers know it exists and how to use it — without this contract itself creating, modifying, or depending on that environment in any way; it only describes it. source/ (including source/project/) is not touched by this contract at all — it remains the permanent, untouched read-only migration reference per ADR-024, not merely 'untouched for now'. No other file in the repository is touched, and no behavior, public API, or structure of the application itself changes.

---

# Current State

project/README.md currently contains the original Tr5-base 'point zero' placeholder: a Purpose section describing an empty project directory, a 'Current capabilities (v0.1)' section stating 'Directory exists. No project code yet', a 'Current limitations' section stating 'Empty until the first contract is implemented', and a 'Planned evolution' section referencing PRINCIPLES.md P1/P15. In reality, following IMPLEMENTATION_CONTRACT_0002's implementation (architecture review round 3: ACCEPTED; implementation review round 1: APPROVED), project/ now contains: send_sms.py (core logic — TOML config loading, phone number normalization/validation, sheet analysis for duplicates/invalid rows, SmsGatewayClient, safe in-place Excel writes via temp file + atomic replace with optional timestamped backup), main.py (CLI with six subcommands: send, send-batch, supplement, find-one, find-sheet, duplicates), streamlit_app.py (web UI: sheet overview, inline editor with save-back-to-Excel, ADD/FIND batch operations, one-off SMS, data quality checks), tests/test_send_sms.py (8 unit tests, manually confirmed by the owner to pass 8/8 after installing dependencies), pyproject.toml, config.example.toml, and SESSION_2026_04_10.md. The owner has also manually created project/.venv, a project-scoped Python virtual environment (gitignored via the root .gitignore's existing unanchored .venv/ pattern; not itself a versioned deliverable), and installed project/'s runtime dependencies into it (openpyxl, pandas, requests, streamlit, per project/pyproject.toml's declared constraints) — separate from the repository's own root framework environment (root requirements.txt: openai-codex, claude-agent-sdk, python-dotenv, pytest, pyaudio, google-genai). source/project/ remains exactly as it was — the untouched, read-only migration reference per ADR-024, including its own copy of the stale placeholder README.md, which is not touched by this contract.

---

# Inputs

The existing (stale) content of project/README.md; the actual current contents of project/main.py, project/streamlit_app.py, project/send_sms.py, project/tests/test_send_sms.py, and project/pyproject.toml as the factual basis for the rewrite; knowledge of the owner-created project/.venv (its purpose, gitignore coverage, and the dependency list it was populated from) as the factual basis for the new development note; the wording convention already used in the existing 'Planned evolution' section (reference to PRINCIPLES.md P1, P15).

---

# Outputs

An updated project/README.md with four top-level sections — Purpose, Current capabilities (v0.1), Current limitations, Planned evolution — whose content accurately reflects the current, post-migration state of project/, with a short development-environment note added inside 'Current capabilities (v0.1)' describing project/.venv. No other file is created or modified; source/ (including source/project/) remains completely untouched.

---

# Functional Requirements

## Point 1

SHALL: Replace the 'Purpose' section of project/README.md so it states that this directory holds the actual, migrated application code for the SMS gateway helper project (a CLI and Streamlit tool for managing GSM gate phone number lists over an SMS gateway), kept separate from the agentic framework/governance layer at the repository root, with contract changes landing here — removing all wording implying the directory is empty or unstarted.

Acceptance criteria:
- project/README.md contains a 'Purpose' (or '## Purpose') section that no longer contains the phrase 'No project code yet' or equivalent 'empty/unstarted' wording
- The Purpose section explicitly names the project as a tool for managing GSM gate phone numbers via an SMS gateway
- The Purpose section still states that this directory is kept separate from the framework/governance layer at the repository root

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 2

SHALL: Replace the 'Current capabilities (v0.1)' section of project/README.md with an accurate list of what exists today: send_sms.py (core logic: config loading, phone number normalization/validation, sheet analysis, SMS gateway client, safe Excel writes with optional backup), main.py (CLI with its six subcommands: send, send-batch, supplement, find-one, find-sheet, duplicates), streamlit_app.py (web UI: sheet overview, inline editor with save-to-Excel, ADD/FIND batch operations, one-off SMS, data quality checks), tests/test_send_sms.py (unit tests for the core logic, confirmed passing), and config.example.toml (configuration template).

Acceptance criteria:
- The 'Current capabilities (v0.1)' section lists send_sms.py, main.py, streamlit_app.py, tests/test_send_sms.py, and config.example.toml by filename with an accurate one-line description of each, matching their actual contents
- The section names all six main.py subcommands (send, send-batch, supplement, find-one, find-sheet, duplicates)
- The section states that the test suite (8 tests) has been confirmed passing
- The section no longer contains the phrase 'Directory exists. No project code yet' or any equivalent placeholder statement

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 3

SHALL: Add a short development-environment note inside the 'Current capabilities (v0.1)' section of project/README.md describing that project/ has its own project-scoped Python virtual environment at project/.venv, separate from the repository's root framework environment, holding project/'s own runtime dependencies, and give a concrete example of how to install into it and run the application/tests against it.

Acceptance criteria:
- The note states that project/.venv is a project-scoped virtual environment, distinct from the repository's root framework environment, and that it is gitignored (already covered by the root .gitignore's existing unanchored .venv/ pattern) rather than a versioned deliverable
- The note states that its dependencies (openpyxl, pandas, requests, streamlit) come from project/pyproject.toml
- The note includes at least one concrete example command showing installation into project/.venv (e.g. `project\.venv\Scripts\python.exe -m pip install openpyxl pandas requests streamlit`) and at least one example command showing how to run the test suite against it (e.g. `project\.venv\Scripts\python.exe -m unittest discover -s tests -v`)
- The note mentions that a local project/config.toml (copied from config.example.toml, itself gitignored per the root .gitignore's config.toml entry) is required to run the application for real

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 4

SHALL: Replace the 'Current limitations' section of project/README.md with the following documented gaps: no automated tests for main.py (CLI argument parsing / exit codes) or for streamlit_app.py; no file locking for concurrent writes to the shared Excel workbook when multiple users save through the Streamlit editor at the same time; CLI commands do not expose a --timeout option unlike the Streamlit UI; the phone number column layout is assumed uniform across all configured gate sheets via a single global column-index constant.

Acceptance criteria:
- The 'Current limitations' section lists all four items above, each as a distinct bullet or sentence
- The section no longer contains the phrase 'Empty until the first contract is implemented against a real project' or any equivalent placeholder statement
- None of the four listed limitations is described as fixed or resolved in this same document (only documented as a current gap)

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 5

SHALL: Update the 'Planned evolution' section of project/README.md so it states that the project grows as further contracts are implemented and that resolving the limitations listed above (concurrent-write protection, CLI/UI parameter parity, per-gate column configuration, additional test coverage) is deferred to those future contracts, while keeping the existing reference to PRINCIPLES.md P1 and P15 on deciding structure only when actually needed.

Acceptance criteria:
- The 'Planned evolution' section references PRINCIPLES.md P1 and P15
- The section explicitly states that the limitations listed in 'Current limitations' are deferred to future contracts rather than addressed here
- The section does not commit to a specific implementation timeline or design for any deferred item

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 6

SHALL: Verify that project/README.md is internally consistent after the rewrite, that it follows the four-section ADR-015 structure plus the one nested development note, and that no other file in the repository was modified as part of this change.

Acceptance criteria:
- A full read-through of project/README.md shows no remaining contradictions between its sections (e.g. no section still implying the directory is empty)
- project/README.md contains exactly the four top-level sections Purpose, Current capabilities (v0.1), Current limitations, Planned evolution, with the development note nested inside Current capabilities rather than as a separate top-level section
- A file-listing check (e.g. Glob across the repository) shows project/README.md as the only file changed by this contract; source/, project/.venv, and every other file under project/ remain unmodified
- No stale placeholder phrases from the original Tr5-base template ('point zero', 'No project code yet', 'Empty until the first contract is implemented') remain anywhere in the file

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

---

# Out of Scope

This contract SHALL NOT modify any file other than project/README.md (source/ and everything under it, including source/project/README.md, remain permanently untouched per ADR-024; project/main.py, project/streamlit_app.py, project/send_sms.py, project/tests/test_send_sms.py, project/pyproject.toml, project/config.example.toml, and project/SESSION_2026_04_10.md must remain unchanged). It SHALL NOT create, modify, populate, or delete project/.venv or project/config.toml — it only documents project/.venv's existing, owner-created state in prose. It SHALL NOT implement, fix, or otherwise act on any of the limitations documented in the README (no file locking, no CLI --timeout flags, no new tests, no per-gate column configuration) — those are documented as known limitations only. It SHALL NOT add sections or claims beyond the four-section ADR-015 structure (Purpose / Current capabilities / Current limitations / Planned evolution) plus the one short development note nested inside Current capabilities. It SHALL NOT write a memory/CHANGE_LOG.md entry (that mechanism applies to light-path fixes only; this change is tracked through the contract itself).

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

### Round 2 — 2026-08-18T14:46:58+02:00 — Verdict: ACCEPTED — Reviewer: `reviewer`

Verified this contract (round 2, after round 1 CHANGES_REQUESTED for targeting the wrong, read-only source/project/README.md) against AGENTS.md, memory/DECISIONS.md, and the live repository state — not against the prior round's text alone.

Target-path fix confirmed: all six points now correctly target project/README.md (the governed, writable README per ADR-015/ADR-016), not source/project/README.md. AGENTS.md and ADR-024 ('source/ ... read-only reference, never edited directly') are satisfied — Out of Scope explicitly excludes source/ and the contract never proposes writing there. Confirmed IMPLEMENTATION_CONTRACT_0002.md is APPROVED with implementation review round 1 APPROVED, so the 'now-migrated' premise this contract's Purpose/Current State rests on is a verified fact, not an assumption.

Independently verified every specific factual claim in Current State and the six points against the actual files, not taken on trust: (1) project/README.md currently reads exactly as described — Purpose describing an empty directory, 'Directory exists. No project code yet', 'Empty until the first contract is implemented', Planned evolution referencing P1/P15. (2) project/ contains exactly send_sms.py, main.py, streamlit_app.py, pyproject.toml, config.example.toml, tests/test_send_sms.py, SESSION_2026_04_10.md, plus README.md (Glob). (3) main.py's six subparsers are exactly send, send-batch, supplement, find-one, find-sheet, duplicates (grep on add_parser). (4) tests/test_send_sms.py contains exactly 8 test_ methods (grep). (5) main.py has no --timeout option; streamlit_app.py exposes a 'HTTP timeout [s]' number_input with DEFAULT_SEND_TIMEOUT in four separate UI flows — confirms the CLI/UI parameter-parity limitation claim in Point 4 is accurate. (6) send_sms.py has no locking primitive around its Excel write path — confirms the concurrent-write limitation claim. (7) GATE_PHONE_COLUMN_INDEX = 1 is one module-level constant applied uniformly to every gate's own sheet in send-batch, find-sheet, and duplicates (SUPPLEMENT_PHONE_COLUMN_INDEX is a separate constant only for the distinct 'Doplnit' sheet) — confirms Point 4's 'single global column-index constant... uniform across all configured gate sheets' claim precisely, not loosely. (8) send_sms.py's write path uses tempfile.NamedTemporaryFile + Path.replace (atomic) plus an optional create_backup_copy() with a timestamped filename — matches Current State's and Point 2's description exactly. (9) project/.venv exists on disk (owner-created, confirmed via Glob) and project/pyproject.toml declares exactly openpyxl, pandas, requests, streamlit — matches Point 3's dependency claim exactly. (10) root .gitignore contains an unanchored '.venv/' entry (line 3, pre-existing) and a 'config.toml' entry (line 11, added by CONTRACT_0002) — matches Point 3's gitignore-coverage claims exactly.

Structural checks: points are individually specific with concrete, checkable acceptance criteria (exact phrases to remove/add); Point 6 explicitly enforces the ADR-015 four-section structure plus one nested note and an Out-of-Scope file-listing check, giving the reviewer an unambiguous implementation-review anchor. Out of Scope is explicit and closes edge cases: no project/.venv or project/config.toml creation, no fixing of the documented limitations, no new sections beyond ADR-015's shape, no memory/CHANGE_LOG.md entry (correctly reasoned: that mechanism is light-path-only per AGENTS.md, and this is a full contract). No backward-compatibility concern (docs-only, no behavior/API change). No destructive command or access beyond the programmer's 'edit' permission profile (Read/Grep/Glob/Edit/Write) is required — Point 6's Glob-based repo-wide check and every other point's Read/Edit are within that profile, unlike an earlier round of CONTRACT_0002 which initially required Bash-only verification steps; this contract has no equivalent gap. No new file/directory name is proposed, so ADR-008's naming convention does not apply. risk_level 'standard' is independently correct: no credentials, no real external calls, no native/hardware libraries, and no personal/real data risk — this is a pure documentation rewrite of an existing file. No escalation warranted.

No blocking issues found. The contract is complete, internally consistent, grounded in independently-verified facts (not assumption), and actionable by the programmer without further clarification.

---

# Future Evolution

The limitations this README documents (concurrent-write protection for the shared Excel workbook, CLI/Streamlit UI parameter parity such as --timeout, per-gate phone-column-layout configuration, test coverage for main.py and streamlit_app.py) are candidates for separate future contracts already identified in the architect's code review queue. This contract only records them as limitations; resolving any of them is deliberately deferred to those later contracts.

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
  "title": "Rewrite project/README.md to reflect the actual, now-migrated project state",
  "status": "READY_FOR_PROGRAMMER",
  "created_by": "architect",
  "assigned_to": "programmer",
  "handoff_to": "programmer",
  "created_at": "2026-08-18T11:25:10+02:00",
  "updated_at": "2026-08-18T14:46:58+02:00",
  "points": [
    {
      "number": 1,
      "assignment": "Replace the 'Purpose' section of project/README.md so it states that this directory holds the actual, migrated application code for the SMS gateway helper project (a CLI and Streamlit tool for managing GSM gate phone number lists over an SMS gateway), kept separate from the agentic framework/governance layer at the repository root, with contract changes landing here — removing all wording implying the directory is empty or unstarted.",
      "acceptance_criteria": [
        "project/README.md contains a 'Purpose' (or '## Purpose') section that no longer contains the phrase 'No project code yet' or equivalent 'empty/unstarted' wording",
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
      "assignment": "Replace the 'Current capabilities (v0.1)' section of project/README.md with an accurate list of what exists today: send_sms.py (core logic: config loading, phone number normalization/validation, sheet analysis, SMS gateway client, safe Excel writes with optional backup), main.py (CLI with its six subcommands: send, send-batch, supplement, find-one, find-sheet, duplicates), streamlit_app.py (web UI: sheet overview, inline editor with save-to-Excel, ADD/FIND batch operations, one-off SMS, data quality checks), tests/test_send_sms.py (unit tests for the core logic, confirmed passing), and config.example.toml (configuration template).",
      "acceptance_criteria": [
        "The 'Current capabilities (v0.1)' section lists send_sms.py, main.py, streamlit_app.py, tests/test_send_sms.py, and config.example.toml by filename with an accurate one-line description of each, matching their actual contents",
        "The section names all six main.py subcommands (send, send-batch, supplement, find-one, find-sheet, duplicates)",
        "The section states that the test suite (8 tests) has been confirmed passing",
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
      "assignment": "Add a short development-environment note inside the 'Current capabilities (v0.1)' section of project/README.md describing that project/ has its own project-scoped Python virtual environment at project/.venv, separate from the repository's root framework environment, holding project/'s own runtime dependencies, and give a concrete example of how to install into it and run the application/tests against it.",
      "acceptance_criteria": [
        "The note states that project/.venv is a project-scoped virtual environment, distinct from the repository's root framework environment, and that it is gitignored (already covered by the root .gitignore's existing unanchored .venv/ pattern) rather than a versioned deliverable",
        "The note states that its dependencies (openpyxl, pandas, requests, streamlit) come from project/pyproject.toml",
        "The note includes at least one concrete example command showing installation into project/.venv (e.g. `project\\.venv\\Scripts\\python.exe -m pip install openpyxl pandas requests streamlit`) and at least one example command showing how to run the test suite against it (e.g. `project\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v`)",
        "The note mentions that a local project/config.toml (copied from config.example.toml, itself gitignored per the root .gitignore's config.toml entry) is required to run the application for real"
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
      "assignment": "Replace the 'Current limitations' section of project/README.md with the following documented gaps: no automated tests for main.py (CLI argument parsing / exit codes) or for streamlit_app.py; no file locking for concurrent writes to the shared Excel workbook when multiple users save through the Streamlit editor at the same time; CLI commands do not expose a --timeout option unlike the Streamlit UI; the phone number column layout is assumed uniform across all configured gate sheets via a single global column-index constant.",
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
      "number": 5,
      "assignment": "Update the 'Planned evolution' section of project/README.md so it states that the project grows as further contracts are implemented and that resolving the limitations listed above (concurrent-write protection, CLI/UI parameter parity, per-gate column configuration, additional test coverage) is deferred to those future contracts, while keeping the existing reference to PRINCIPLES.md P1 and P15 on deciding structure only when actually needed.",
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
      "number": 6,
      "assignment": "Verify that project/README.md is internally consistent after the rewrite, that it follows the four-section ADR-015 structure plus the one nested development note, and that no other file in the repository was modified as part of this change.",
      "acceptance_criteria": [
        "A full read-through of project/README.md shows no remaining contradictions between its sections (e.g. no section still implying the directory is empty)",
        "project/README.md contains exactly the four top-level sections Purpose, Current capabilities (v0.1), Current limitations, Planned evolution, with the development note nested inside Current capabilities rather than as a separate top-level section",
        "A file-listing check (e.g. Glob across the repository) shows project/README.md as the only file changed by this contract; source/, project/.venv, and every other file under project/ remain unmodified",
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
  "purpose": "project/README.md still shows the generic Tr5-base placeholder text (\"Directory exists. No project code yet\"), even though project/ now holds a working, migrated, and manually-verified (8/8 tests passing) CLI and Streamlit tool for managing GSM gate phone number lists — moved there by IMPLEMENTATION_CONTRACT_0002 from the read-only source/project/ reference. This mismatch was originally flagged during the architect's code review as a documentation-debt item (P6: Current State must reflect facts); the first attempt at fixing it (this same contract's round 1) mistakenly targeted the read-only source/project/README.md, which architecture review correctly rejected per ADR-024 ('source/ stays untouched, never edited directly'). Now that the migration has landed and been verified, fixing project/README.md gives anyone opening the actual, governed project directory an accurate first read of what exists there, instead of text that contradicts the repository.",
  "intent": "This change only rewrites the content of project/README.md so its Purpose / Current capabilities / Current limitations / Planned evolution sections match what is actually in project/ today, post-migration. It documents known gaps (missing CLI/UI test coverage, no concurrent-write protection on the shared Excel workbook, CLI/UI parameter parity, the single global phone-column-index assumption) as limitations to read, not as work to perform now — those remain separate, already-queued follow-up contracts. It additionally documents, for the first time, the project-scoped project/.venv the owner created and populated manually (per IMPLEMENTATION_CONTRACT_0002's Out of Scope, since the programmer has no Bash access to do this itself), so future readers know it exists and how to use it — without this contract itself creating, modifying, or depending on that environment in any way; it only describes it. source/ (including source/project/) is not touched by this contract at all — it remains the permanent, untouched read-only migration reference per ADR-024, not merely 'untouched for now'. No other file in the repository is touched, and no behavior, public API, or structure of the application itself changes.",
  "current_state": "project/README.md currently contains the original Tr5-base 'point zero' placeholder: a Purpose section describing an empty project directory, a 'Current capabilities (v0.1)' section stating 'Directory exists. No project code yet', a 'Current limitations' section stating 'Empty until the first contract is implemented', and a 'Planned evolution' section referencing PRINCIPLES.md P1/P15. In reality, following IMPLEMENTATION_CONTRACT_0002's implementation (architecture review round 3: ACCEPTED; implementation review round 1: APPROVED), project/ now contains: send_sms.py (core logic — TOML config loading, phone number normalization/validation, sheet analysis for duplicates/invalid rows, SmsGatewayClient, safe in-place Excel writes via temp file + atomic replace with optional timestamped backup), main.py (CLI with six subcommands: send, send-batch, supplement, find-one, find-sheet, duplicates), streamlit_app.py (web UI: sheet overview, inline editor with save-back-to-Excel, ADD/FIND batch operations, one-off SMS, data quality checks), tests/test_send_sms.py (8 unit tests, manually confirmed by the owner to pass 8/8 after installing dependencies), pyproject.toml, config.example.toml, and SESSION_2026_04_10.md. The owner has also manually created project/.venv, a project-scoped Python virtual environment (gitignored via the root .gitignore's existing unanchored .venv/ pattern; not itself a versioned deliverable), and installed project/'s runtime dependencies into it (openpyxl, pandas, requests, streamlit, per project/pyproject.toml's declared constraints) — separate from the repository's own root framework environment (root requirements.txt: openai-codex, claude-agent-sdk, python-dotenv, pytest, pyaudio, google-genai). source/project/ remains exactly as it was — the untouched, read-only migration reference per ADR-024, including its own copy of the stale placeholder README.md, which is not touched by this contract.",
  "inputs": "The existing (stale) content of project/README.md; the actual current contents of project/main.py, project/streamlit_app.py, project/send_sms.py, project/tests/test_send_sms.py, and project/pyproject.toml as the factual basis for the rewrite; knowledge of the owner-created project/.venv (its purpose, gitignore coverage, and the dependency list it was populated from) as the factual basis for the new development note; the wording convention already used in the existing 'Planned evolution' section (reference to PRINCIPLES.md P1, P15).",
  "outputs": "An updated project/README.md with four top-level sections — Purpose, Current capabilities (v0.1), Current limitations, Planned evolution — whose content accurately reflects the current, post-migration state of project/, with a short development-environment note added inside 'Current capabilities (v0.1)' describing project/.venv. No other file is created or modified; source/ (including source/project/) remains completely untouched.",
  "out_of_scope": "This contract SHALL NOT modify any file other than project/README.md (source/ and everything under it, including source/project/README.md, remain permanently untouched per ADR-024; project/main.py, project/streamlit_app.py, project/send_sms.py, project/tests/test_send_sms.py, project/pyproject.toml, project/config.example.toml, and project/SESSION_2026_04_10.md must remain unchanged). It SHALL NOT create, modify, populate, or delete project/.venv or project/config.toml — it only documents project/.venv's existing, owner-created state in prose. It SHALL NOT implement, fix, or otherwise act on any of the limitations documented in the README (no file locking, no CLI --timeout flags, no new tests, no per-gate column configuration) — those are documented as known limitations only. It SHALL NOT add sections or claims beyond the four-section ADR-015 structure (Purpose / Current capabilities / Current limitations / Planned evolution) plus the one short development note nested inside Current capabilities. It SHALL NOT write a memory/CHANGE_LOG.md entry (that mechanism applies to light-path fixes only; this change is tracked through the contract itself).",
  "future_evolution": "The limitations this README documents (concurrent-write protection for the shared Excel workbook, CLI/Streamlit UI parameter parity such as --timeout, per-gate phone-column-layout configuration, test coverage for main.py and streamlit_app.py) are candidates for separate future contracts already identified in the architect's code review queue. This contract only records them as limitations; resolving any of them is deliberately deferred to those later contracts.",
  "lessons_learned": "",
  "architecture_review_rounds": [
    {
      "round": 1,
      "date": "2026-08-18T11:27:08+02:00",
      "verdict": "CHANGES_REQUESTED",
      "reviewer": "reviewer",
      "findings": "Checked the contract's factual claims about source/project against the actual files (main.py's six subparsers — send, send-batch, supplement, find-one, find-sheet, duplicates — verified via grep; tests/test_send_sms.py's 8 test methods verified by name; config.toml gitignored via source/project/.gitignore verified). Those facts are accurate, so P6 ('Current State contains facts') is satisfied at the content level.\n\nHowever, the contract's target path is architecturally wrong. `AGENTS.md` states explicitly: '`source/` holds the original/input source code of an existing project being migrated onto this pipeline — read-only reference, never edited directly; migrated/new code lands in `project/` instead — see ADR-024.' ADR-024 in memory/DECISIONS.md confirms the same: source/ is 'copied in as-is and kept untouched'; migrated/rewritten code lands in `project/` contract by contract. `memory/CURRENT_STATE.md` (the Discovery Engine's own generated inventory) confirms `source/project/` is a full nested copy of a prior bod-nula-based project (including its own `.git`, its own `agents/`, `memory/`, `contracts/`, and its own `project/` subdirectory holding the real SMS app) — exactly the 'original/input source being migrated' that ADR-024 describes, not a place where documentation is meant to be actively maintained going forward.\n\nAll five points of this contract, and its Outputs/Out-of-Scope sections, are built entirely around rewriting `source/project/README.md` — a file inside that read-only reference tree. This directly contradicts the explicit 'never edited directly' rule. The top-level `project/README.md` (which already exists, still holding the generic point-zero placeholder, and is exactly the file ADR-015/ADR-016 designate for describing 'the actual application code being built through the contract pipeline') was not touched or even considered by this contract — meaning the underlying documentation-debt problem (P6) is real, but the fix as scoped will leave the actually-governed, non-read-only README (`project/README.md`) still wrong while illegitimately editing a file that policy says must stay untouched. This is not a matter of style; it is the premise of the whole contract, so it cannot be salvaged by tweaking a single point's wording.\n\nOther checks: points are individually specific and independently verifiable (acceptance criteria reference concrete phrases to remove/add), no naming-convention violation (README.md), no destructive commands or access beyond `edit`, no backward-compatibility concern (docs-only), and risk_level `standard` is correctly assessed (no credentials, no external calls, no native/hardware libraries, no personal/real data — config.toml stays gitignored). These are not blocking issues; only the target-path violation is.\n\nRecommendation for revision: either retarget every point at `project/README.md` (documenting current_state honestly, i.e. that the real SMS/Streamlit code has not yet been migrated there and still lives only in the read-only `source/project/` reference — which is a materially different and smaller truth than what this draft currently proposes to write), or scope this as part of an actual migration contract that moves the code from `source/project/` into `project/` per ADR-024's intended flow. Either path requires the architect to rewrite the contract, not the programmer to interpret around a target it cannot legally write to."
    },
    {
      "round": 2,
      "date": "2026-08-18T14:46:58+02:00",
      "verdict": "ACCEPTED",
      "reviewer": "reviewer",
      "findings": "Verified this contract (round 2, after round 1 CHANGES_REQUESTED for targeting the wrong, read-only source/project/README.md) against AGENTS.md, memory/DECISIONS.md, and the live repository state — not against the prior round's text alone.\n\nTarget-path fix confirmed: all six points now correctly target project/README.md (the governed, writable README per ADR-015/ADR-016), not source/project/README.md. AGENTS.md and ADR-024 ('source/ ... read-only reference, never edited directly') are satisfied — Out of Scope explicitly excludes source/ and the contract never proposes writing there. Confirmed IMPLEMENTATION_CONTRACT_0002.md is APPROVED with implementation review round 1 APPROVED, so the 'now-migrated' premise this contract's Purpose/Current State rests on is a verified fact, not an assumption.\n\nIndependently verified every specific factual claim in Current State and the six points against the actual files, not taken on trust: (1) project/README.md currently reads exactly as described — Purpose describing an empty directory, 'Directory exists. No project code yet', 'Empty until the first contract is implemented', Planned evolution referencing P1/P15. (2) project/ contains exactly send_sms.py, main.py, streamlit_app.py, pyproject.toml, config.example.toml, tests/test_send_sms.py, SESSION_2026_04_10.md, plus README.md (Glob). (3) main.py's six subparsers are exactly send, send-batch, supplement, find-one, find-sheet, duplicates (grep on add_parser). (4) tests/test_send_sms.py contains exactly 8 test_ methods (grep). (5) main.py has no --timeout option; streamlit_app.py exposes a 'HTTP timeout [s]' number_input with DEFAULT_SEND_TIMEOUT in four separate UI flows — confirms the CLI/UI parameter-parity limitation claim in Point 4 is accurate. (6) send_sms.py has no locking primitive around its Excel write path — confirms the concurrent-write limitation claim. (7) GATE_PHONE_COLUMN_INDEX = 1 is one module-level constant applied uniformly to every gate's own sheet in send-batch, find-sheet, and duplicates (SUPPLEMENT_PHONE_COLUMN_INDEX is a separate constant only for the distinct 'Doplnit' sheet) — confirms Point 4's 'single global column-index constant... uniform across all configured gate sheets' claim precisely, not loosely. (8) send_sms.py's write path uses tempfile.NamedTemporaryFile + Path.replace (atomic) plus an optional create_backup_copy() with a timestamped filename — matches Current State's and Point 2's description exactly. (9) project/.venv exists on disk (owner-created, confirmed via Glob) and project/pyproject.toml declares exactly openpyxl, pandas, requests, streamlit — matches Point 3's dependency claim exactly. (10) root .gitignore contains an unanchored '.venv/' entry (line 3, pre-existing) and a 'config.toml' entry (line 11, added by CONTRACT_0002) — matches Point 3's gitignore-coverage claims exactly.\n\nStructural checks: points are individually specific with concrete, checkable acceptance criteria (exact phrases to remove/add); Point 6 explicitly enforces the ADR-015 four-section structure plus one nested note and an Out-of-Scope file-listing check, giving the reviewer an unambiguous implementation-review anchor. Out of Scope is explicit and closes edge cases: no project/.venv or project/config.toml creation, no fixing of the documented limitations, no new sections beyond ADR-015's shape, no memory/CHANGE_LOG.md entry (correctly reasoned: that mechanism is light-path-only per AGENTS.md, and this is a full contract). No backward-compatibility concern (docs-only, no behavior/API change). No destructive command or access beyond the programmer's 'edit' permission profile (Read/Grep/Glob/Edit/Write) is required — Point 6's Glob-based repo-wide check and every other point's Read/Edit are within that profile, unlike an earlier round of CONTRACT_0002 which initially required Bash-only verification steps; this contract has no equivalent gap. No new file/directory name is proposed, so ADR-008's naming convention does not apply. risk_level 'standard' is independently correct: no credentials, no real external calls, no native/hardware libraries, and no personal/real data risk — this is a pure documentation rewrite of an existing file. No escalation warranted.\n\nNo blocking issues found. The contract is complete, internally consistent, grounded in independently-verified facts (not assumption), and actionable by the programmer without further clarification."
    }
  ],
  "completion_notes": "",
  "implementation_review_rounds": []
}
CONTRACT-META -->
