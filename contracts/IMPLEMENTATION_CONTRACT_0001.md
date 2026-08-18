# IMPLEMENTATION_CONTRACT_0001

Status: APPROVED

---

# Workflow

- Created by: `architect`
- Reviewer (both review gates): `reviewer`
- Implementer: `programmer`
- Risk level: `standard`
- Currently with: `owner`
- Handed off to: `owner`
- Created at: `2026-08-18T11:25:10+02:00`
- Updated at: `2026-08-18T14:49:12+02:00`

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

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-18T14:48:06+02:00._

Replaced the Purpose section: it now names the project explicitly as a CLI/Streamlit tool for managing GSM gate phone number lists over an SMS gateway, states this directory holds the actual migrated application code with contract changes landing here, keeps the statement that it is separate from the root framework/governance layer, and removes all 'empty/unstarted' wording. Also updated the source/ reference to describe it as read-only migration reference per ADR-024.

Files touched:
- `project/README.md`

Tests:
- Grep verification of main.py's six subparsers (send, send-batch, supplement, find-one, find-sheet, duplicates)
- Grep verification of 8 test_ methods in project/tests/test_send_sms.py
- Grep confirming no stale placeholder phrases remain in project/README.md
- Glob confirming project/README.md was the only file changed

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-18T14:49:12+02:00._

Purpose section (lines 3-16) names the project explicitly as 'a CLI and Streamlit tool for managing GSM gate phone number lists over an SMS gateway', states this directory holds the actual migrated application code with contract changes landing here, and states it is kept separate from the framework/governance layer at the repository root, listing concrete root-level files/dirs. No 'No project code yet' or equivalent empty/unstarted wording remains. Matches acceptance criteria exactly.

## Point 2

SHALL: Replace the 'Current capabilities (v0.1)' section of project/README.md with an accurate list of what exists today: send_sms.py (core logic: config loading, phone number normalization/validation, sheet analysis, SMS gateway client, safe Excel writes with optional backup), main.py (CLI with its six subcommands: send, send-batch, supplement, find-one, find-sheet, duplicates), streamlit_app.py (web UI: sheet overview, inline editor with save-to-Excel, ADD/FIND batch operations, one-off SMS, data quality checks), tests/test_send_sms.py (unit tests for the core logic, confirmed passing), and config.example.toml (configuration template).

Acceptance criteria:
- The 'Current capabilities (v0.1)' section lists send_sms.py, main.py, streamlit_app.py, tests/test_send_sms.py, and config.example.toml by filename with an accurate one-line description of each, matching their actual contents
- The section names all six main.py subcommands (send, send-batch, supplement, find-one, find-sheet, duplicates)
- The section states that the test suite (8 tests) has been confirmed passing
- The section no longer contains the phrase 'Directory exists. No project code yet' or any equivalent placeholder statement

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-18T14:48:06+02:00._

Replaced 'Current capabilities (v0.1)' with an accurate itemized list: send_sms.py (config loading, phone normalization/validation, sheet analysis, SmsGatewayClient, safe Excel writes with backup), main.py naming all six subcommands (send, send-batch, supplement, find-one, find-sheet, duplicates) verified via grep against main.py's add_parser calls, streamlit_app.py (sheet overview, inline editor with save-to-Excel, ADD/FIND batch ops, one-off SMS, data quality checks), tests/test_send_sms.py stating the 8-test suite is confirmed passing (verified 8 test_ methods via grep), and config.example.toml. Removed the 'Directory exists. No project code yet' placeholder.

Files touched:
- `project/README.md`

Tests:
- Grep for add_parser in project/main.py — confirmed 6 subcommands
- Grep for def test_ in project/tests/test_send_sms.py — confirmed 8 tests

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-18T14:49:12+02:00._

'Current capabilities (v0.1)' (lines 18-38) lists send_sms.py, main.py, streamlit_app.py, tests/test_send_sms.py, and config.example.toml, each with an accurate one-line description verified against actual file contents (confirmed send_sms.py's config loading/normalization/sheet analysis/SmsGatewayClient/atomic Excel write with backup via direct code read; confirmed main.py's six subcommands via grep on add_parser: send, send-batch, supplement, find-one, find-sheet, duplicates — all named; confirmed 8 test_ methods via grep, and the README states the 8-test suite was confirmed passing by the owner). No 'Directory exists. No project code yet' placeholder remains.

## Point 3

SHALL: Add a short development-environment note inside the 'Current capabilities (v0.1)' section of project/README.md describing that project/ has its own project-scoped Python virtual environment at project/.venv, separate from the repository's root framework environment, holding project/'s own runtime dependencies, and give a concrete example of how to install into it and run the application/tests against it.

Acceptance criteria:
- The note states that project/.venv is a project-scoped virtual environment, distinct from the repository's root framework environment, and that it is gitignored (already covered by the root .gitignore's existing unanchored .venv/ pattern) rather than a versioned deliverable
- The note states that its dependencies (openpyxl, pandas, requests, streamlit) come from project/pyproject.toml
- The note includes at least one concrete example command showing installation into project/.venv (e.g. `project\.venv\Scripts\python.exe -m pip install openpyxl pandas requests streamlit`) and at least one example command showing how to run the test suite against it (e.g. `project\.venv\Scripts\python.exe -m unittest discover -s tests -v`)
- The note mentions that a local project/config.toml (copied from config.example.toml, itself gitignored per the root .gitignore's config.toml entry) is required to run the application for real

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-18T14:48:06+02:00._

Added a 'Development environment' sub-section nested inside 'Current capabilities (v0.1)' describing project/.venv as a project-scoped virtual environment separate from the root framework environment, noting it is gitignored via the existing unanchored .venv/ pattern rather than versioned, listing its dependencies (openpyxl, pandas, requests, streamlit) as sourced from project/pyproject.toml (verified by reading that file), giving concrete pip-install and unittest-discover example commands, and mentioning that a local project/config.toml copied from config.example.toml (itself gitignored) is required to run the app for real.

Files touched:
- `project/README.md`

Tests:
- Read project/pyproject.toml to confirm dependency list matches

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-18T14:49:12+02:00._

'Development environment' sub-section (lines 40-60), nested inside Current capabilities, states project/.venv is a project-scoped venv distinct from the root framework environment, states it is gitignored via the existing unanchored .venv/ pattern (confirmed present at .gitignore line 3) rather than versioned, lists dependencies openpyxl/pandas/requests/streamlit sourced from project/pyproject.toml (confirmed these are exactly the four dependencies declared there), gives a concrete pip-install command and a concrete unittest-discover command, and mentions that a local project/config.toml copied from config.example.toml (itself gitignored, confirmed at .gitignore line 11) is required to run the app for real. All four acceptance criteria satisfied.

## Point 4

SHALL: Replace the 'Current limitations' section of project/README.md with the following documented gaps: no automated tests for main.py (CLI argument parsing / exit codes) or for streamlit_app.py; no file locking for concurrent writes to the shared Excel workbook when multiple users save through the Streamlit editor at the same time; CLI commands do not expose a --timeout option unlike the Streamlit UI; the phone number column layout is assumed uniform across all configured gate sheets via a single global column-index constant.

Acceptance criteria:
- The 'Current limitations' section lists all four items above, each as a distinct bullet or sentence
- The section no longer contains the phrase 'Empty until the first contract is implemented against a real project' or any equivalent placeholder statement
- None of the four listed limitations is described as fixed or resolved in this same document (only documented as a current gap)

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-18T14:48:06+02:00._

Replaced 'Current limitations' with the four documented gaps as distinct bullets: missing tests for main.py/streamlit_app.py, no file locking for concurrent Excel writes, no CLI --timeout option (unlike the Streamlit UI), and the single global phone-column-index constant assumption. Removed the old placeholder sentence. None of the four items is described as fixed.

Files touched:
- `project/README.md`

Tests:
- Grep verification of main.py's six subparsers (send, send-batch, supplement, find-one, find-sheet, duplicates)
- Grep verification of 8 test_ methods in project/tests/test_send_sms.py
- Grep confirming no stale placeholder phrases remain in project/README.md
- Glob confirming project/README.md was the only file changed

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-18T14:49:12+02:00._

'Current limitations' (lines 62-70) lists all four required items as distinct bullets: missing tests for main.py/streamlit_app.py, no file locking for concurrent Excel writes (confirmed no locking primitive in send_sms.py's write path), no CLI --timeout option unlike Streamlit UI (confirmed: 0 timeout occurrences in main.py vs. 22 in streamlit_app.py), and the single global phone-column-index constant (confirmed GATE_PHONE_COLUMN_INDEX = 1 is applied uniformly across send-batch/find-sheet/duplicates operations on gate sheets). No placeholder phrase remains, and none of the four items is described as fixed.

## Point 5

SHALL: Update the 'Planned evolution' section of project/README.md so it states that the project grows as further contracts are implemented and that resolving the limitations listed above (concurrent-write protection, CLI/UI parameter parity, per-gate column configuration, additional test coverage) is deferred to those future contracts, while keeping the existing reference to PRINCIPLES.md P1 and P15 on deciding structure only when actually needed.

Acceptance criteria:
- The 'Planned evolution' section references PRINCIPLES.md P1 and P15
- The section explicitly states that the limitations listed in 'Current limitations' are deferred to future contracts rather than addressed here
- The section does not commit to a specific implementation timeline or design for any deferred item

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-18T14:48:06+02:00._

Updated 'Planned evolution' to state the project grows as further contracts are implemented, explicitly defers resolving the four listed limitations (concurrent-write protection, CLI/UI parameter parity, per-gate column configuration, additional test coverage) to future contracts, keeps the PRINCIPLES.md P1/P15 reference, and does not commit to any timeline or design for the deferred items.

Files touched:
- `project/README.md`

Tests:
- Grep verification of main.py's six subparsers (send, send-batch, supplement, find-one, find-sheet, duplicates)
- Grep verification of 8 test_ methods in project/tests/test_send_sms.py
- Grep confirming no stale placeholder phrases remain in project/README.md
- Glob confirming project/README.md was the only file changed

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-18T14:49:12+02:00._

'Planned evolution' (lines 72-79) states the project grows as further contracts are implemented, explicitly defers concurrent-write protection, CLI/UI parameter parity, per-gate column configuration, and additional test coverage to future contracts, keeps the PRINCIPLES.md P1/P15 reference, and commits to no specific timeline or design for any deferred item.

## Point 6

SHALL: Verify that project/README.md is internally consistent after the rewrite, that it follows the four-section ADR-015 structure plus the one nested development note, and that no other file in the repository was modified as part of this change.

Acceptance criteria:
- A full read-through of project/README.md shows no remaining contradictions between its sections (e.g. no section still implying the directory is empty)
- project/README.md contains exactly the four top-level sections Purpose, Current capabilities (v0.1), Current limitations, Planned evolution, with the development note nested inside Current capabilities rather than as a separate top-level section
- A file-listing check (e.g. Glob across the repository) shows project/README.md as the only file changed by this contract; source/, project/.venv, and every other file under project/ remain unmodified
- No stale placeholder phrases from the original Tr5-base template ('point zero', 'No project code yet', 'Empty until the first contract is implemented') remain anywhere in the file

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-18T14:48:06+02:00._

Read through the final project/README.md: it is internally consistent with no remaining implication that the directory is empty. It contains exactly the four top-level sections (Purpose, Current capabilities (v0.1), Current limitations, Planned evolution) with the development-environment note nested as a sub-section under Current capabilities, not a top-level section. Verified via Grep that none of the stale placeholder phrases ('point zero', 'No project code yet', 'Empty until the first contract is implemented') remain anywhere in the file. Verified via Glob that project/README.md and project/SESSION_2026_04_10.md are the only .md files under project/, and no other file under project/ or source/ was written to during this task — only project/README.md was edited.

Files touched:
- `project/README.md`

Tests:
- Grep 'point zero|No project code yet|Empty until the first contract is implemented' on project/README.md — no matches
- Glob project/*.md — confirms only README.md and SESSION_2026_04_10.md present, no unintended new files

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-18T14:49:12+02:00._

Full read-through shows no internal contradiction and no remaining implication the directory is empty. The file contains exactly the four top-level ## sections (Purpose, Current capabilities (v0.1), Current limitations, Planned evolution) with 'Development environment' as a ### sub-section nested inside Current capabilities, not a separate top-level section. Grep for 'point zero|No project code yet|Empty until the first contract is implemented' returns no matches. Glob of project/* confirms only README.md was modified by this contract; send_sms.py, main.py, streamlit_app.py, pyproject.toml, config.example.toml, tests/test_send_sms.py, and SESSION_2026_04_10.md are unchanged (also unchanged per the discovery diff, which lists only project/README.md as a substantive content change).

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

Rewrote project/README.md to replace the stale Tr5-base placeholder with content accurately describing the actual, migrated SMS gateway helper tool (send_sms.py, main.py with its six subcommands, streamlit_app.py, tests/test_send_sms.py, config.example.toml), added a development-environment note about the owner-created project/.venv, documented the four known limitations, and updated the Planned evolution section to defer those limitations to future contracts while keeping the PRINCIPLES.md P1/P15 reference. Only project/README.md was touched; source/ (including source/project/) and every other file under project/ remain unmodified, per ADR-024 and the contract's Out of Scope.

---

# Implementation Review

### Round 1 — 2026-08-18T14:49:12+02:00 — Verdict: APPROVED — Reviewer: `reviewer`

Read the final project/README.md and independently re-verified every factual claim in it against the actual source files (project/main.py's six add_parser subcommands, tests/test_send_sms.py's 8 test_ methods, project/pyproject.toml's four dependencies, send_sms.py's GATE_PHONE_COLUMN_INDEX/SUPPLEMENT_PHONE_COLUMN_INDEX constants, its NamedTemporaryFile+Path.replace atomic-write path with optional create_backup_copy, streamlit_app.py's 22 timeout-related occurrences vs. main.py having none, and the root .gitignore's .venv/ and config.toml entries). All six points match their accepted acceptance criteria exactly, no stale placeholder phrases remain, the document has exactly the four ADR-015 top-level sections plus one nested development-environment note, and no file other than project/README.md was substantively changed.

Out of Scope check: OK — Discovery diff lists three changed files: project/README.md, agents/architect/WORKING_STATE.md, and agents/programmer/runtime/session.log. project/README.md is the one file this contract's points call for and its content matches every point above. agents/architect/WORKING_STATE.md is explicitly machine-generated per Tr5-base decision 10 ('Generated automatically from the live contract queue on every state change ... do not edit by hand') and its content is only the current contract-queue status line, not a manual edit by the programmer. agents/programmer/runtime/session.log is an append-only tool-call log; the entries from 14:47:24 onward (this contract's session) show only Read/Glob/Grep on project/README.md, project/pyproject.toml, project/main.py, and project/tests/test_send_sms.py plus a single Write to project/README.md — all read-only verification and the one in-scope write, consistent with the contract's points. The earlier log lines at 12:44-12:48 belong to the prior contract (IMPLEMENTATION_CONTRACT_0002)'s session appended to the same cumulative file and are not new work performed under this contract. No file under source/, no project/.venv, no project/config.toml, and no other file under project/ was created, modified, or deleted. Nothing beyond the contract's points was touched.

---

# Lessons Learned

_Not filled in._

---

<!-- CONTRACT-META
{
  "number": 1,
  "title": "Rewrite project/README.md to reflect the actual, now-migrated project state",
  "status": "APPROVED",
  "created_by": "architect",
  "assigned_to": "owner",
  "handoff_to": "owner",
  "created_at": "2026-08-18T11:25:10+02:00",
  "updated_at": "2026-08-18T14:49:12+02:00",
  "points": [
    {
      "number": 1,
      "assignment": "Replace the 'Purpose' section of project/README.md so it states that this directory holds the actual, migrated application code for the SMS gateway helper project (a CLI and Streamlit tool for managing GSM gate phone number lists over an SMS gateway), kept separate from the agentic framework/governance layer at the repository root, with contract changes landing here — removing all wording implying the directory is empty or unstarted.",
      "acceptance_criteria": [
        "project/README.md contains a 'Purpose' (or '## Purpose') section that no longer contains the phrase 'No project code yet' or equivalent 'empty/unstarted' wording",
        "The Purpose section explicitly names the project as a tool for managing GSM gate phone numbers via an SMS gateway",
        "The Purpose section still states that this directory is kept separate from the framework/governance layer at the repository root"
      ],
      "programmer_note": "Replaced the Purpose section: it now names the project explicitly as a CLI/Streamlit tool for managing GSM gate phone number lists over an SMS gateway, states this directory holds the actual migrated application code with contract changes landing here, keeps the statement that it is separate from the root framework/governance layer, and removes all 'empty/unstarted' wording. Also updated the source/ reference to describe it as read-only migration reference per ADR-024.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T14:48:06+02:00",
      "programmer_files": [
        "project/README.md"
      ],
      "programmer_tests": [
        "Grep verification of main.py's six subparsers (send, send-batch, supplement, find-one, find-sheet, duplicates)",
        "Grep verification of 8 test_ methods in project/tests/test_send_sms.py",
        "Grep confirming no stale placeholder phrases remain in project/README.md",
        "Glob confirming project/README.md was the only file changed"
      ],
      "reviewer_note": "Purpose section (lines 3-16) names the project explicitly as 'a CLI and Streamlit tool for managing GSM gate phone number lists over an SMS gateway', states this directory holds the actual migrated application code with contract changes landing here, and states it is kept separate from the framework/governance layer at the repository root, listing concrete root-level files/dirs. No 'No project code yet' or equivalent empty/unstarted wording remains. Matches acceptance criteria exactly.",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-18T14:49:12+02:00",
      "status": "APPROVED"
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
      "programmer_note": "Replaced 'Current capabilities (v0.1)' with an accurate itemized list: send_sms.py (config loading, phone normalization/validation, sheet analysis, SmsGatewayClient, safe Excel writes with backup), main.py naming all six subcommands (send, send-batch, supplement, find-one, find-sheet, duplicates) verified via grep against main.py's add_parser calls, streamlit_app.py (sheet overview, inline editor with save-to-Excel, ADD/FIND batch ops, one-off SMS, data quality checks), tests/test_send_sms.py stating the 8-test suite is confirmed passing (verified 8 test_ methods via grep), and config.example.toml. Removed the 'Directory exists. No project code yet' placeholder.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T14:48:06+02:00",
      "programmer_files": [
        "project/README.md"
      ],
      "programmer_tests": [
        "Grep for add_parser in project/main.py — confirmed 6 subcommands",
        "Grep for def test_ in project/tests/test_send_sms.py — confirmed 8 tests"
      ],
      "reviewer_note": "'Current capabilities (v0.1)' (lines 18-38) lists send_sms.py, main.py, streamlit_app.py, tests/test_send_sms.py, and config.example.toml, each with an accurate one-line description verified against actual file contents (confirmed send_sms.py's config loading/normalization/sheet analysis/SmsGatewayClient/atomic Excel write with backup via direct code read; confirmed main.py's six subcommands via grep on add_parser: send, send-batch, supplement, find-one, find-sheet, duplicates — all named; confirmed 8 test_ methods via grep, and the README states the 8-test suite was confirmed passing by the owner). No 'Directory exists. No project code yet' placeholder remains.",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-18T14:49:12+02:00",
      "status": "APPROVED"
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
      "programmer_note": "Added a 'Development environment' sub-section nested inside 'Current capabilities (v0.1)' describing project/.venv as a project-scoped virtual environment separate from the root framework environment, noting it is gitignored via the existing unanchored .venv/ pattern rather than versioned, listing its dependencies (openpyxl, pandas, requests, streamlit) as sourced from project/pyproject.toml (verified by reading that file), giving concrete pip-install and unittest-discover example commands, and mentioning that a local project/config.toml copied from config.example.toml (itself gitignored) is required to run the app for real.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T14:48:06+02:00",
      "programmer_files": [
        "project/README.md"
      ],
      "programmer_tests": [
        "Read project/pyproject.toml to confirm dependency list matches"
      ],
      "reviewer_note": "'Development environment' sub-section (lines 40-60), nested inside Current capabilities, states project/.venv is a project-scoped venv distinct from the root framework environment, states it is gitignored via the existing unanchored .venv/ pattern (confirmed present at .gitignore line 3) rather than versioned, lists dependencies openpyxl/pandas/requests/streamlit sourced from project/pyproject.toml (confirmed these are exactly the four dependencies declared there), gives a concrete pip-install command and a concrete unittest-discover command, and mentions that a local project/config.toml copied from config.example.toml (itself gitignored, confirmed at .gitignore line 11) is required to run the app for real. All four acceptance criteria satisfied.",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-18T14:49:12+02:00",
      "status": "APPROVED"
    },
    {
      "number": 4,
      "assignment": "Replace the 'Current limitations' section of project/README.md with the following documented gaps: no automated tests for main.py (CLI argument parsing / exit codes) or for streamlit_app.py; no file locking for concurrent writes to the shared Excel workbook when multiple users save through the Streamlit editor at the same time; CLI commands do not expose a --timeout option unlike the Streamlit UI; the phone number column layout is assumed uniform across all configured gate sheets via a single global column-index constant.",
      "acceptance_criteria": [
        "The 'Current limitations' section lists all four items above, each as a distinct bullet or sentence",
        "The section no longer contains the phrase 'Empty until the first contract is implemented against a real project' or any equivalent placeholder statement",
        "None of the four listed limitations is described as fixed or resolved in this same document (only documented as a current gap)"
      ],
      "programmer_note": "Replaced 'Current limitations' with the four documented gaps as distinct bullets: missing tests for main.py/streamlit_app.py, no file locking for concurrent Excel writes, no CLI --timeout option (unlike the Streamlit UI), and the single global phone-column-index constant assumption. Removed the old placeholder sentence. None of the four items is described as fixed.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T14:48:06+02:00",
      "programmer_files": [
        "project/README.md"
      ],
      "programmer_tests": [
        "Grep verification of main.py's six subparsers (send, send-batch, supplement, find-one, find-sheet, duplicates)",
        "Grep verification of 8 test_ methods in project/tests/test_send_sms.py",
        "Grep confirming no stale placeholder phrases remain in project/README.md",
        "Glob confirming project/README.md was the only file changed"
      ],
      "reviewer_note": "'Current limitations' (lines 62-70) lists all four required items as distinct bullets: missing tests for main.py/streamlit_app.py, no file locking for concurrent Excel writes (confirmed no locking primitive in send_sms.py's write path), no CLI --timeout option unlike Streamlit UI (confirmed: 0 timeout occurrences in main.py vs. 22 in streamlit_app.py), and the single global phone-column-index constant (confirmed GATE_PHONE_COLUMN_INDEX = 1 is applied uniformly across send-batch/find-sheet/duplicates operations on gate sheets). No placeholder phrase remains, and none of the four items is described as fixed.",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-18T14:49:12+02:00",
      "status": "APPROVED"
    },
    {
      "number": 5,
      "assignment": "Update the 'Planned evolution' section of project/README.md so it states that the project grows as further contracts are implemented and that resolving the limitations listed above (concurrent-write protection, CLI/UI parameter parity, per-gate column configuration, additional test coverage) is deferred to those future contracts, while keeping the existing reference to PRINCIPLES.md P1 and P15 on deciding structure only when actually needed.",
      "acceptance_criteria": [
        "The 'Planned evolution' section references PRINCIPLES.md P1 and P15",
        "The section explicitly states that the limitations listed in 'Current limitations' are deferred to future contracts rather than addressed here",
        "The section does not commit to a specific implementation timeline or design for any deferred item"
      ],
      "programmer_note": "Updated 'Planned evolution' to state the project grows as further contracts are implemented, explicitly defers resolving the four listed limitations (concurrent-write protection, CLI/UI parameter parity, per-gate column configuration, additional test coverage) to future contracts, keeps the PRINCIPLES.md P1/P15 reference, and does not commit to any timeline or design for the deferred items.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T14:48:06+02:00",
      "programmer_files": [
        "project/README.md"
      ],
      "programmer_tests": [
        "Grep verification of main.py's six subparsers (send, send-batch, supplement, find-one, find-sheet, duplicates)",
        "Grep verification of 8 test_ methods in project/tests/test_send_sms.py",
        "Grep confirming no stale placeholder phrases remain in project/README.md",
        "Glob confirming project/README.md was the only file changed"
      ],
      "reviewer_note": "'Planned evolution' (lines 72-79) states the project grows as further contracts are implemented, explicitly defers concurrent-write protection, CLI/UI parameter parity, per-gate column configuration, and additional test coverage to future contracts, keeps the PRINCIPLES.md P1/P15 reference, and commits to no specific timeline or design for any deferred item.",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-18T14:49:12+02:00",
      "status": "APPROVED"
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
      "programmer_note": "Read through the final project/README.md: it is internally consistent with no remaining implication that the directory is empty. It contains exactly the four top-level sections (Purpose, Current capabilities (v0.1), Current limitations, Planned evolution) with the development-environment note nested as a sub-section under Current capabilities, not a top-level section. Verified via Grep that none of the stale placeholder phrases ('point zero', 'No project code yet', 'Empty until the first contract is implemented') remain anywhere in the file. Verified via Glob that project/README.md and project/SESSION_2026_04_10.md are the only .md files under project/, and no other file under project/ or source/ was written to during this task — only project/README.md was edited.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T14:48:06+02:00",
      "programmer_files": [
        "project/README.md"
      ],
      "programmer_tests": [
        "Grep 'point zero|No project code yet|Empty until the first contract is implemented' on project/README.md — no matches",
        "Glob project/*.md — confirms only README.md and SESSION_2026_04_10.md present, no unintended new files"
      ],
      "reviewer_note": "Full read-through shows no internal contradiction and no remaining implication the directory is empty. The file contains exactly the four top-level ## sections (Purpose, Current capabilities (v0.1), Current limitations, Planned evolution) with 'Development environment' as a ### sub-section nested inside Current capabilities, not a separate top-level section. Grep for 'point zero|No project code yet|Empty until the first contract is implemented' returns no matches. Glob of project/* confirms only README.md was modified by this contract; send_sms.py, main.py, streamlit_app.py, pyproject.toml, config.example.toml, tests/test_send_sms.py, and SESSION_2026_04_10.md are unchanged (also unchanged per the discovery diff, which lists only project/README.md as a substantive content change).",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-18T14:49:12+02:00",
      "status": "APPROVED"
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
  "completion_notes": "Rewrote project/README.md to replace the stale Tr5-base placeholder with content accurately describing the actual, migrated SMS gateway helper tool (send_sms.py, main.py with its six subcommands, streamlit_app.py, tests/test_send_sms.py, config.example.toml), added a development-environment note about the owner-created project/.venv, documented the four known limitations, and updated the Planned evolution section to defer those limitations to future contracts while keeping the PRINCIPLES.md P1/P15 reference. Only project/README.md was touched; source/ (including source/project/) and every other file under project/ remain unmodified, per ADR-024 and the contract's Out of Scope.",
  "implementation_review_rounds": [
    {
      "round": 1,
      "date": "2026-08-18T14:49:12+02:00",
      "verdict": "APPROVED",
      "reviewer": "reviewer",
      "summary": "Read the final project/README.md and independently re-verified every factual claim in it against the actual source files (project/main.py's six add_parser subcommands, tests/test_send_sms.py's 8 test_ methods, project/pyproject.toml's four dependencies, send_sms.py's GATE_PHONE_COLUMN_INDEX/SUPPLEMENT_PHONE_COLUMN_INDEX constants, its NamedTemporaryFile+Path.replace atomic-write path with optional create_backup_copy, streamlit_app.py's 22 timeout-related occurrences vs. main.py having none, and the root .gitignore's .venv/ and config.toml entries). All six points match their accepted acceptance criteria exactly, no stale placeholder phrases remain, the document has exactly the four ADR-015 top-level sections plus one nested development-environment note, and no file other than project/README.md was substantively changed.",
      "out_of_scope_ok": true,
      "out_of_scope_findings": "Discovery diff lists three changed files: project/README.md, agents/architect/WORKING_STATE.md, and agents/programmer/runtime/session.log. project/README.md is the one file this contract's points call for and its content matches every point above. agents/architect/WORKING_STATE.md is explicitly machine-generated per Tr5-base decision 10 ('Generated automatically from the live contract queue on every state change ... do not edit by hand') and its content is only the current contract-queue status line, not a manual edit by the programmer. agents/programmer/runtime/session.log is an append-only tool-call log; the entries from 14:47:24 onward (this contract's session) show only Read/Glob/Grep on project/README.md, project/pyproject.toml, project/main.py, and project/tests/test_send_sms.py plus a single Write to project/README.md — all read-only verification and the one in-scope write, consistent with the contract's points. The earlier log lines at 12:44-12:48 belong to the prior contract (IMPLEMENTATION_CONTRACT_0002)'s session appended to the same cumulative file and are not new work performed under this contract. No file under source/, no project/.venv, no project/config.toml, and no other file under project/ was created, modified, or deleted. Nothing beyond the contract's points was touched.",
      "reviews": [
        {
          "point": 1,
          "status": "APPROVED",
          "review": "Purpose section (lines 3-16) names the project explicitly as 'a CLI and Streamlit tool for managing GSM gate phone number lists over an SMS gateway', states this directory holds the actual migrated application code with contract changes landing here, and states it is kept separate from the framework/governance layer at the repository root, listing concrete root-level files/dirs. No 'No project code yet' or equivalent empty/unstarted wording remains. Matches acceptance criteria exactly."
        },
        {
          "point": 2,
          "status": "APPROVED",
          "review": "'Current capabilities (v0.1)' (lines 18-38) lists send_sms.py, main.py, streamlit_app.py, tests/test_send_sms.py, and config.example.toml, each with an accurate one-line description verified against actual file contents (confirmed send_sms.py's config loading/normalization/sheet analysis/SmsGatewayClient/atomic Excel write with backup via direct code read; confirmed main.py's six subcommands via grep on add_parser: send, send-batch, supplement, find-one, find-sheet, duplicates — all named; confirmed 8 test_ methods via grep, and the README states the 8-test suite was confirmed passing by the owner). No 'Directory exists. No project code yet' placeholder remains."
        },
        {
          "point": 3,
          "status": "APPROVED",
          "review": "'Development environment' sub-section (lines 40-60), nested inside Current capabilities, states project/.venv is a project-scoped venv distinct from the root framework environment, states it is gitignored via the existing unanchored .venv/ pattern (confirmed present at .gitignore line 3) rather than versioned, lists dependencies openpyxl/pandas/requests/streamlit sourced from project/pyproject.toml (confirmed these are exactly the four dependencies declared there), gives a concrete pip-install command and a concrete unittest-discover command, and mentions that a local project/config.toml copied from config.example.toml (itself gitignored, confirmed at .gitignore line 11) is required to run the app for real. All four acceptance criteria satisfied."
        },
        {
          "point": 4,
          "status": "APPROVED",
          "review": "'Current limitations' (lines 62-70) lists all four required items as distinct bullets: missing tests for main.py/streamlit_app.py, no file locking for concurrent Excel writes (confirmed no locking primitive in send_sms.py's write path), no CLI --timeout option unlike Streamlit UI (confirmed: 0 timeout occurrences in main.py vs. 22 in streamlit_app.py), and the single global phone-column-index constant (confirmed GATE_PHONE_COLUMN_INDEX = 1 is applied uniformly across send-batch/find-sheet/duplicates operations on gate sheets). No placeholder phrase remains, and none of the four items is described as fixed."
        },
        {
          "point": 5,
          "status": "APPROVED",
          "review": "'Planned evolution' (lines 72-79) states the project grows as further contracts are implemented, explicitly defers concurrent-write protection, CLI/UI parameter parity, per-gate column configuration, and additional test coverage to future contracts, keeps the PRINCIPLES.md P1/P15 reference, and commits to no specific timeline or design for any deferred item."
        },
        {
          "point": 6,
          "status": "APPROVED",
          "review": "Full read-through shows no internal contradiction and no remaining implication the directory is empty. The file contains exactly the four top-level ## sections (Purpose, Current capabilities (v0.1), Current limitations, Planned evolution) with 'Development environment' as a ### sub-section nested inside Current capabilities, not a separate top-level section. Grep for 'point zero|No project code yet|Empty until the first contract is implemented' returns no matches. Glob of project/* confirms only README.md was modified by this contract; send_sms.py, main.py, streamlit_app.py, pyproject.toml, config.example.toml, tests/test_send_sms.py, and SESSION_2026_04_10.md are unchanged (also unchanged per the discovery diff, which lists only project/README.md as a substantive content change)."
        }
      ]
    }
  ]
}
CONTRACT-META -->
