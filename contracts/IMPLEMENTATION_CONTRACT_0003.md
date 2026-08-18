# IMPLEMENTATION_CONTRACT_0003

Status: READY_FOR_PROGRAMMER

---

# Workflow

- Created by: `architect`
- Reviewer (both review gates): `reviewer`
- Implementer: `programmer`
- Risk level: `standard`
- Currently with: `programmer`
- Handed off to: `programmer`
- Created at: `2026-08-18T15:08:37+02:00`
- Updated at: `2026-08-18T15:10:29+02:00`

---

# Title

Detect and reject concurrent writes to the shared Excel workbook

---

# Purpose

The shared Excel workbook referenced by config.excel_path is typically a network file used by multiple people through the Streamlit editor. save_sheet_numbers() currently reads, modifies, and rewrites the whole workbook with no protection against two overlapping saves — if two people save around the same time, one save silently overwrites the other's changes with no warning, which for gate access phone number lists is a real risk of losing legitimate entries or, worse, losing a legitimate removal that gets silently reintroduced. This change makes an overlapping save fail loudly and safely instead of corrupting data silently, protecting the integrity of safety-relevant gate access data.

---

# Intent

This implements a minimal file-based mutual-exclusion mechanism scoped strictly to save_sheet_numbers()'s write path: a sidecar lock file next to the workbook, created atomically (no new third-party dependency needed) before any read of the workbook, removed afterward regardless of outcome. It deliberately implements detect-and-reject, not a full multi-writer merge, retry queue, or optimistic-locking/versioning scheme — a rejected save simply asks the person to retry, the same way it would if the file were open in Excel (an error case save_sheet_numbers() already raises today). streamlit_app.py needs no code change: render_sheet_editor() already wraps its call to save_sheet_numbers() in a try/except SpreadsheetError that displays the error via st.error(), so the new rejection surfaces to the user automatically. This also updates project/README.md (added by IMPLEMENTATION_CONTRACT_0001) so its documentation stays factually accurate once this lands — the now-resolved concurrent-write gap moves out of 'Current limitations' into 'Current capabilities', replaced by the narrower, still-real residual limitation that a lock left behind by a hard-crashed process is not automatically cleared. That staleness-recovery question, and any richer concurrency model, are deliberately left for a later contract if it turns out to matter in practice.

---

# Current State

project/send_sms.py's save_sheet_numbers() (module-level function) reads the target workbook via load_workbook(BytesIO(workbook_path.read_bytes())), modifies the target column's cells, and writes the result through a NamedTemporaryFile followed by an atomic Path.replace() onto workbook_path — with no locking of any kind at any step. Nothing prevents two overlapping calls (e.g. from two separate Streamlit browser sessions) from each reading the same original content, each modifying it independently, and each overwriting the other's temp-file replace, silently losing whichever write happened first. project/README.md's 'Current limitations' section (added by IMPLEMENTATION_CONTRACT_0001) already documents this exact gap: 'no file locking for concurrent writes to the shared Excel workbook when multiple users save through the Streamlit editor at the same time.' project/streamlit_app.py's render_sheet_editor() calls save_sheet_numbers() inside a try/except SpreadsheetError block that calls st.error(str(exc)) on failure — this exception path already exists and requires no change. project/tests/test_send_sms.py has one existing test for save_sheet_numbers(), test_save_sheet_numbers_normalizes_and_preserves_other_columns, which builds a real temporary XLSX workbook with openpyxl.Workbook() and a temporary config.toml inside a tempfile.TemporaryDirectory() — the pattern new tests should follow. The programmer's Claude permission_profile is 'edit' (Read, Grep, Glob, Edit, Write only, confirmed in agents/agent.py and agents/programmer/config.json) — no Bash tool is available, so the programmer cannot execute the test suite itself; per IMPLEMENTATION_CONTRACT_0002's established and reviewer-accepted precedent, actually running the suite is a manual follow-up step for the owner.

---

# Inputs

The existing save_sheet_numbers() implementation and its single call site (project/streamlit_app.py's render_sheet_editor()); config.AppConfig.excel_path (the workbook's Path); project/tests/test_send_sms.py's existing tempfile-based workbook/config fixture pattern; project/README.md's current 'Current capabilities (v0.1)' and 'Current limitations' sections.

---

# Outputs

Modified project/send_sms.py: save_sheet_numbers() gains lock-file detection (reject an overlapping save) and guaranteed lock-file cleanup, with no change to its existing public signature or return type (SheetSaveResult). Modified project/tests/test_send_sms.py: three new unit tests covering the new behavior. Modified project/README.md: one bullet moved from 'Current limitations' to 'Current capabilities (v0.1)', and one new, narrower bullet added to 'Current limitations' describing the residual stale-lock gap. No other file is created or modified; project/main.py, project/config.example.toml, project/pyproject.toml, and everything under source/ remain untouched.

---

# Functional Requirements

## Point 1

SHALL: Add atomic lock-file detection to save_sheet_numbers() in project/send_sms.py, running before any read or modification of the target workbook: compute a lock path of the form '<workbook file name>.lock' in the workbook's own directory, and attempt to create it using an exclusive/atomic creation mode (e.g. Python's `open(path, "x")`) as the function's first interaction with the workbook's directory, before `workbook_path.read_bytes()`/`load_workbook` is called. If that creation raises FileExistsError, raise SpreadsheetError with a message stating that a save to that workbook is already in progress, without reading, loading, or writing the workbook at all.

Acceptance criteria:
- save_sheet_numbers() computes the lock path as the workbook's file name with '.lock' appended, located in the same directory as the workbook (e.g. for 'gates.xlsx' the lock path is 'gates.xlsx.lock')
- The exclusive lock-file creation happens before any call to workbook_path.read_bytes() or load_workbook() in the function body
- If the lock file already exists (FileExistsError on exclusive creation), save_sheet_numbers() raises SpreadsheetError with a message stating a save is already in progress, and workbook_path.read_bytes()/load_workbook() and the temp-file write are never reached
- If the lock file did not previously exist, save_sheet_numbers() proceeds through its existing read/modify/write logic (backup creation, column update loop, temp file + atomic replace) unchanged

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 2

SHALL: Ensure the lock file created in the previous point is always removed once the save attempt finishes, whether it succeeds or raises any exception during the read/modify/write logic, but never remove a pre-existing lock file that this call itself did not create (the 'already locked' rejection path must not delete the lock it detected).

Acceptance criteria:
- Lock-file removal after a save attempt is implemented so it runs on both the success path and every exception path raised during the read/modify/write logic (e.g. via try/finally or equivalent), covering SpreadsheetError for a missing sheet and PermissionError/OSError translated to SpreadsheetError
- After a successful call to save_sheet_numbers(), the lock file no longer exists on disk
- After a call to save_sheet_numbers() that fails for a reason unrelated to locking (e.g. the target sheet name is not found in the workbook), the lock file no longer exists on disk
- When save_sheet_numbers() rejects a call because the lock file already existed (per the previous point), that pre-existing lock file is left in place, not deleted, by the rejecting call

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 3

SHALL: Add three new unit tests to project/tests/test_send_sms.py covering the new locking behavior, following the existing tempfile-based workbook/config fixture pattern used by test_save_sheet_numbers_normalizes_and_preserves_other_columns.

Acceptance criteria:
- Three new test methods are added, distinctly named for their scenario (e.g. test_save_sheet_numbers_removes_lock_after_success, test_save_sheet_numbers_rejects_when_lock_file_present, test_save_sheet_numbers_removes_lock_after_unrelated_failure)
- Each new test uses the existing tempfile.TemporaryDirectory()-based real-workbook/config fixture pattern, not a mocked filesystem
- Reading the 'removes_lock_after_success' test confirms it performs a normal save and then asserts the '<workbook>.lock' file does not exist afterward
- Reading the 'rejects_when_lock_file_present' test confirms it pre-creates the '<workbook>.lock' file, calls save_sheet_numbers(), asserts a SpreadsheetError is raised, and asserts the workbook file's bytes on disk are unchanged from before the call
- Reading the 'removes_lock_after_unrelated_failure' test confirms it triggers an existing unrelated failure path (e.g. a sheet_name that does not exist in the workbook), asserts a SpreadsheetError is raised, and asserts the '<workbook>.lock' file does not exist afterward
- Actually executing the full test suite (11 tests total after this addition) and confirming all pass is explicitly left as a manual follow-up for the owner, per this contract's Out of Scope, since the programmer has no Bash access to run it

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 4

SHALL: Add a bullet to the 'Current capabilities (v0.1)' section of project/README.md describing that save_sheet_numbers() now detects and rejects an overlapping concurrent save via a sidecar lock file, instead of silently allowing one save to overwrite another.

Acceptance criteria:
- The 'Current capabilities (v0.1)' section contains a new bullet stating that concurrent saves to the shared Excel workbook are detected and safely rejected (not silently overwritten), naming the mechanism as a sidecar lock file
- The new bullet does not claim to solve stale-lock recovery or any form of multi-writer merge
- No existing bullet in 'Current capabilities (v0.1)' is removed or altered by this point

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 5

SHALL: Update the 'Current limitations' section of project/README.md: remove the existing bullet stating there is no file locking for concurrent Excel writes, and replace it with a narrower bullet stating that a lock file left behind by a process that crashes mid-save is not automatically cleared (no staleness/TTL recovery), so such a lock would need manual removal.

Acceptance criteria:
- The 'Current limitations' section no longer contains the original 'no file locking for concurrent writes to the shared Excel workbook' bullet
- The 'Current limitations' section contains a new bullet specifically about stale-lock recovery not being automatic, as described above
- The other three limitations bullets (missing CLI/UI test coverage, no CLI --timeout parity, the single global phone-column-index assumption) remain present and unaltered

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

---

# Out of Scope

This contract SHALL NOT implement a full multi-writer merge, conflict-resolution UI, or optimistic-locking/version-stamp scheme — only detect-and-reject of an overlapping save. It SHALL NOT modify project/streamlit_app.py — its existing SpreadsheetError handling already covers the new rejection path. It SHALL NOT add automatic retry/backoff logic for a rejected save; the caller must retry manually. It SHALL NOT implement stale-lock recovery (no TTL/staleness detection for a lock file left behind by a crashed process) — this residual gap is documented in project/README.md, not solved. It SHALL NOT add any new third-party dependency; the lock mechanism uses only Python's standard library. It SHALL NOT modify any file other than project/send_sms.py, project/tests/test_send_sms.py, and project/README.md. It SHALL NOT execute the test suite as part of the programmer's own verification — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash access to run `python -m unittest`/pytest. The programmer instead verifies each new test's correctness by reading and tracing its logic against points 1 and 2's implementation; actually running the full suite (11 tests) and confirming they all pass is an explicit manual follow-up for the owner after this contract is committed, mirroring IMPLEMENTATION_CONTRACT_0002's established precedent.

---

# Acceptance Criteria

Acceptance criteria are listed per point in the Functional Requirements section.

---

# Architecture Review

### Round 1 — 2026-08-18T15:10:29+02:00 — Verdict: ACCEPTED — Reviewer: `reviewer`

Verified against AGENTS.md, PRINCIPLES.md, and memory/DECISIONS.md, plus the actual current code (project/send_sms.py, project/streamlit_app.py, project/tests/test_send_sms.py, project/README.md, project/config.example.toml).

1. Purpose/Intent is a real, documented need, not a premature abstraction: project/README.md's 'Current limitations' already contains the exact quoted bullet about missing file locking for concurrent writes (added by CONTRACT_0001), config.example.toml's excel_path is a real UNC network share path, confirming the 'shared workbook used by multiple people' framing. The contract deliberately scopes to detect-and-reject only, explicitly deferring stale-lock recovery and richer concurrency models to a future contract — consistent with P1 ('architecture defines direction, implementation reflects today's understanding') and P15 (standards extracted from real need, not invented in advance).

2. Current State is factually accurate, verified by reading project/send_sms.py's save_sheet_numbers(): confirmed it reads via load_workbook(BytesIO(workbook_path.read_bytes())), writes via NamedTemporaryFile + atomic Path.replace(), with zero locking today. project/streamlit_app.py line 428 confirms render_sheet_editor() already wraps the call in try/except SpreadsheetError with st.error() — the contract's claim that streamlit_app.py needs no change holds. project/tests/test_send_sms.py has exactly one existing save_sheet_numbers() test using the described tempfile/openpyxl pattern; current suite is 8 tests, so 'the new suite is 11 tests' (Point 3) is arithmetically correct.

3. Points 1-5 are actionable in order (implement lock creation → guaranteed cleanup → tests → doc capabilities → doc limitations) and each has concrete, mechanically checkable acceptance criteria (specific lock path format, explicit ordering relative to read_bytes()/load_workbook(), named test scenarios, exact README section edits, confirmation the other 3 limitations bullets stay untouched — verified against the actual 4-bullet 'Current limitations' section in project/README.md).

4. Out of Scope is explicit and covers the realistic edge cases: no merge/versioning, no streamlit_app.py change, no retry/backoff, no stale-lock TTL recovery, no new dependency, no file outside the three named ones, and explicitly no test execution by the programmer (with a stated reason and precedent).

5. No backward-compatibility break without justification: SheetSaveResult and the function's public signature are explicitly unchanged; the only behavior change (rejecting an overlapping save) is the entire justified point of the contract.

6. No destructive commands and no access beyond the programmer's 'edit' permission profile: confirmed in agents/agent.py (CLAUDE_EDIT_TOOLS = Read/Grep/Glob/Edit/Write, no Bash) that the programmer genuinely cannot run the test suite; the contract correctly treats this as a manual owner follow-up, mirroring the precedent already recorded in memory/DECISIONS.md for IMPLEMENTATION_CONTRACT_0002. No file outside project/ is touched, matching AGENTS.md's project/-scoping rule (ADR-022).

7. No new file/directory names are introduced that need naming-convention review; the '<workbook>.lock' sidecar path is a runtime artifact next to a network-share Excel file, not a repository path, so no gitignore/naming concern applies (P5 is not triggered).

8. risk_level: checked against Tr5-base decision 7's criteria (real credentials/API keys, real external calls, native/hardware libraries, risk of landing personal/real data in git). This contract adds only a standard-library file lock around existing local/network file I/O, no new external calls, no credentials, no native libraries, and the three new tests follow the existing pattern of using synthetic fake phone numbers in a tempfile.TemporaryDirectory() (never touching the real, personal-data-bearing workbook or landing anything in git). 'standard' is appropriate; no escalation warranted.

9. Minor, non-blocking observation: Point 1's acceptance criteria only pin the lock-creation ordering relative to workbook_path.read_bytes()/load_workbook(), not relative to the existing workbook_path.exists() check or the optional create_backup_copy() step, and does not specify how a non-FileExistsError (e.g. PermissionError) during lock creation should be surfaced. This is a small, reasonably-inferable implementation detail (existing code already wraps comparable errors into SpreadsheetError), not a real architectural gap per P13 — it does not require rewriting the contract, but the reviewer will check during implementation review how the programmer handled it.

Overall: complete enough to implement without further clarification, consistent with existing conventions and the project's principles. Accepted as written.

---

# Future Evolution

Stale-lock recovery (e.g. a TTL/age check on the lock file so a crashed process's leftover lock doesn't block saves indefinitely) is deferred to a future contract if it turns out to be a real problem in practice, not designed now (P1/P15). A richer concurrency model (optimistic locking with version stamps, true multi-writer merge, or a queueing mechanism) is likewise deferred. The other three limitations already documented in project/README.md (CLI/UI test coverage, CLI --timeout parity, the single global phone-column-index assumption) remain untouched by this contract and stay queued for their own separate future contracts.

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
  "number": 3,
  "title": "Detect and reject concurrent writes to the shared Excel workbook",
  "status": "READY_FOR_PROGRAMMER",
  "created_by": "architect",
  "assigned_to": "programmer",
  "handoff_to": "programmer",
  "created_at": "2026-08-18T15:08:37+02:00",
  "updated_at": "2026-08-18T15:10:29+02:00",
  "points": [
    {
      "number": 1,
      "assignment": "Add atomic lock-file detection to save_sheet_numbers() in project/send_sms.py, running before any read or modification of the target workbook: compute a lock path of the form '<workbook file name>.lock' in the workbook's own directory, and attempt to create it using an exclusive/atomic creation mode (e.g. Python's `open(path, \"x\")`) as the function's first interaction with the workbook's directory, before `workbook_path.read_bytes()`/`load_workbook` is called. If that creation raises FileExistsError, raise SpreadsheetError with a message stating that a save to that workbook is already in progress, without reading, loading, or writing the workbook at all.",
      "acceptance_criteria": [
        "save_sheet_numbers() computes the lock path as the workbook's file name with '.lock' appended, located in the same directory as the workbook (e.g. for 'gates.xlsx' the lock path is 'gates.xlsx.lock')",
        "The exclusive lock-file creation happens before any call to workbook_path.read_bytes() or load_workbook() in the function body",
        "If the lock file already exists (FileExistsError on exclusive creation), save_sheet_numbers() raises SpreadsheetError with a message stating a save is already in progress, and workbook_path.read_bytes()/load_workbook() and the temp-file write are never reached",
        "If the lock file did not previously exist, save_sheet_numbers() proceeds through its existing read/modify/write logic (backup creation, column update loop, temp file + atomic replace) unchanged"
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
      "assignment": "Ensure the lock file created in the previous point is always removed once the save attempt finishes, whether it succeeds or raises any exception during the read/modify/write logic, but never remove a pre-existing lock file that this call itself did not create (the 'already locked' rejection path must not delete the lock it detected).",
      "acceptance_criteria": [
        "Lock-file removal after a save attempt is implemented so it runs on both the success path and every exception path raised during the read/modify/write logic (e.g. via try/finally or equivalent), covering SpreadsheetError for a missing sheet and PermissionError/OSError translated to SpreadsheetError",
        "After a successful call to save_sheet_numbers(), the lock file no longer exists on disk",
        "After a call to save_sheet_numbers() that fails for a reason unrelated to locking (e.g. the target sheet name is not found in the workbook), the lock file no longer exists on disk",
        "When save_sheet_numbers() rejects a call because the lock file already existed (per the previous point), that pre-existing lock file is left in place, not deleted, by the rejecting call"
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
      "assignment": "Add three new unit tests to project/tests/test_send_sms.py covering the new locking behavior, following the existing tempfile-based workbook/config fixture pattern used by test_save_sheet_numbers_normalizes_and_preserves_other_columns.",
      "acceptance_criteria": [
        "Three new test methods are added, distinctly named for their scenario (e.g. test_save_sheet_numbers_removes_lock_after_success, test_save_sheet_numbers_rejects_when_lock_file_present, test_save_sheet_numbers_removes_lock_after_unrelated_failure)",
        "Each new test uses the existing tempfile.TemporaryDirectory()-based real-workbook/config fixture pattern, not a mocked filesystem",
        "Reading the 'removes_lock_after_success' test confirms it performs a normal save and then asserts the '<workbook>.lock' file does not exist afterward",
        "Reading the 'rejects_when_lock_file_present' test confirms it pre-creates the '<workbook>.lock' file, calls save_sheet_numbers(), asserts a SpreadsheetError is raised, and asserts the workbook file's bytes on disk are unchanged from before the call",
        "Reading the 'removes_lock_after_unrelated_failure' test confirms it triggers an existing unrelated failure path (e.g. a sheet_name that does not exist in the workbook), asserts a SpreadsheetError is raised, and asserts the '<workbook>.lock' file does not exist afterward",
        "Actually executing the full test suite (11 tests total after this addition) and confirming all pass is explicitly left as a manual follow-up for the owner, per this contract's Out of Scope, since the programmer has no Bash access to run it"
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
      "assignment": "Add a bullet to the 'Current capabilities (v0.1)' section of project/README.md describing that save_sheet_numbers() now detects and rejects an overlapping concurrent save via a sidecar lock file, instead of silently allowing one save to overwrite another.",
      "acceptance_criteria": [
        "The 'Current capabilities (v0.1)' section contains a new bullet stating that concurrent saves to the shared Excel workbook are detected and safely rejected (not silently overwritten), naming the mechanism as a sidecar lock file",
        "The new bullet does not claim to solve stale-lock recovery or any form of multi-writer merge",
        "No existing bullet in 'Current capabilities (v0.1)' is removed or altered by this point"
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
      "assignment": "Update the 'Current limitations' section of project/README.md: remove the existing bullet stating there is no file locking for concurrent Excel writes, and replace it with a narrower bullet stating that a lock file left behind by a process that crashes mid-save is not automatically cleared (no staleness/TTL recovery), so such a lock would need manual removal.",
      "acceptance_criteria": [
        "The 'Current limitations' section no longer contains the original 'no file locking for concurrent writes to the shared Excel workbook' bullet",
        "The 'Current limitations' section contains a new bullet specifically about stale-lock recovery not being automatic, as described above",
        "The other three limitations bullets (missing CLI/UI test coverage, no CLI --timeout parity, the single global phone-column-index assumption) remain present and unaltered"
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
  "purpose": "The shared Excel workbook referenced by config.excel_path is typically a network file used by multiple people through the Streamlit editor. save_sheet_numbers() currently reads, modifies, and rewrites the whole workbook with no protection against two overlapping saves — if two people save around the same time, one save silently overwrites the other's changes with no warning, which for gate access phone number lists is a real risk of losing legitimate entries or, worse, losing a legitimate removal that gets silently reintroduced. This change makes an overlapping save fail loudly and safely instead of corrupting data silently, protecting the integrity of safety-relevant gate access data.",
  "intent": "This implements a minimal file-based mutual-exclusion mechanism scoped strictly to save_sheet_numbers()'s write path: a sidecar lock file next to the workbook, created atomically (no new third-party dependency needed) before any read of the workbook, removed afterward regardless of outcome. It deliberately implements detect-and-reject, not a full multi-writer merge, retry queue, or optimistic-locking/versioning scheme — a rejected save simply asks the person to retry, the same way it would if the file were open in Excel (an error case save_sheet_numbers() already raises today). streamlit_app.py needs no code change: render_sheet_editor() already wraps its call to save_sheet_numbers() in a try/except SpreadsheetError that displays the error via st.error(), so the new rejection surfaces to the user automatically. This also updates project/README.md (added by IMPLEMENTATION_CONTRACT_0001) so its documentation stays factually accurate once this lands — the now-resolved concurrent-write gap moves out of 'Current limitations' into 'Current capabilities', replaced by the narrower, still-real residual limitation that a lock left behind by a hard-crashed process is not automatically cleared. That staleness-recovery question, and any richer concurrency model, are deliberately left for a later contract if it turns out to matter in practice.",
  "current_state": "project/send_sms.py's save_sheet_numbers() (module-level function) reads the target workbook via load_workbook(BytesIO(workbook_path.read_bytes())), modifies the target column's cells, and writes the result through a NamedTemporaryFile followed by an atomic Path.replace() onto workbook_path — with no locking of any kind at any step. Nothing prevents two overlapping calls (e.g. from two separate Streamlit browser sessions) from each reading the same original content, each modifying it independently, and each overwriting the other's temp-file replace, silently losing whichever write happened first. project/README.md's 'Current limitations' section (added by IMPLEMENTATION_CONTRACT_0001) already documents this exact gap: 'no file locking for concurrent writes to the shared Excel workbook when multiple users save through the Streamlit editor at the same time.' project/streamlit_app.py's render_sheet_editor() calls save_sheet_numbers() inside a try/except SpreadsheetError block that calls st.error(str(exc)) on failure — this exception path already exists and requires no change. project/tests/test_send_sms.py has one existing test for save_sheet_numbers(), test_save_sheet_numbers_normalizes_and_preserves_other_columns, which builds a real temporary XLSX workbook with openpyxl.Workbook() and a temporary config.toml inside a tempfile.TemporaryDirectory() — the pattern new tests should follow. The programmer's Claude permission_profile is 'edit' (Read, Grep, Glob, Edit, Write only, confirmed in agents/agent.py and agents/programmer/config.json) — no Bash tool is available, so the programmer cannot execute the test suite itself; per IMPLEMENTATION_CONTRACT_0002's established and reviewer-accepted precedent, actually running the suite is a manual follow-up step for the owner.",
  "inputs": "The existing save_sheet_numbers() implementation and its single call site (project/streamlit_app.py's render_sheet_editor()); config.AppConfig.excel_path (the workbook's Path); project/tests/test_send_sms.py's existing tempfile-based workbook/config fixture pattern; project/README.md's current 'Current capabilities (v0.1)' and 'Current limitations' sections.",
  "outputs": "Modified project/send_sms.py: save_sheet_numbers() gains lock-file detection (reject an overlapping save) and guaranteed lock-file cleanup, with no change to its existing public signature or return type (SheetSaveResult). Modified project/tests/test_send_sms.py: three new unit tests covering the new behavior. Modified project/README.md: one bullet moved from 'Current limitations' to 'Current capabilities (v0.1)', and one new, narrower bullet added to 'Current limitations' describing the residual stale-lock gap. No other file is created or modified; project/main.py, project/config.example.toml, project/pyproject.toml, and everything under source/ remain untouched.",
  "out_of_scope": "This contract SHALL NOT implement a full multi-writer merge, conflict-resolution UI, or optimistic-locking/version-stamp scheme — only detect-and-reject of an overlapping save. It SHALL NOT modify project/streamlit_app.py — its existing SpreadsheetError handling already covers the new rejection path. It SHALL NOT add automatic retry/backoff logic for a rejected save; the caller must retry manually. It SHALL NOT implement stale-lock recovery (no TTL/staleness detection for a lock file left behind by a crashed process) — this residual gap is documented in project/README.md, not solved. It SHALL NOT add any new third-party dependency; the lock mechanism uses only Python's standard library. It SHALL NOT modify any file other than project/send_sms.py, project/tests/test_send_sms.py, and project/README.md. It SHALL NOT execute the test suite as part of the programmer's own verification — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash access to run `python -m unittest`/pytest. The programmer instead verifies each new test's correctness by reading and tracing its logic against points 1 and 2's implementation; actually running the full suite (11 tests) and confirming they all pass is an explicit manual follow-up for the owner after this contract is committed, mirroring IMPLEMENTATION_CONTRACT_0002's established precedent.",
  "future_evolution": "Stale-lock recovery (e.g. a TTL/age check on the lock file so a crashed process's leftover lock doesn't block saves indefinitely) is deferred to a future contract if it turns out to be a real problem in practice, not designed now (P1/P15). A richer concurrency model (optimistic locking with version stamps, true multi-writer merge, or a queueing mechanism) is likewise deferred. The other three limitations already documented in project/README.md (CLI/UI test coverage, CLI --timeout parity, the single global phone-column-index assumption) remain untouched by this contract and stay queued for their own separate future contracts.",
  "lessons_learned": "",
  "architecture_review_rounds": [
    {
      "round": 1,
      "date": "2026-08-18T15:10:29+02:00",
      "verdict": "ACCEPTED",
      "reviewer": "reviewer",
      "findings": "Verified against AGENTS.md, PRINCIPLES.md, and memory/DECISIONS.md, plus the actual current code (project/send_sms.py, project/streamlit_app.py, project/tests/test_send_sms.py, project/README.md, project/config.example.toml).\n\n1. Purpose/Intent is a real, documented need, not a premature abstraction: project/README.md's 'Current limitations' already contains the exact quoted bullet about missing file locking for concurrent writes (added by CONTRACT_0001), config.example.toml's excel_path is a real UNC network share path, confirming the 'shared workbook used by multiple people' framing. The contract deliberately scopes to detect-and-reject only, explicitly deferring stale-lock recovery and richer concurrency models to a future contract — consistent with P1 ('architecture defines direction, implementation reflects today's understanding') and P15 (standards extracted from real need, not invented in advance).\n\n2. Current State is factually accurate, verified by reading project/send_sms.py's save_sheet_numbers(): confirmed it reads via load_workbook(BytesIO(workbook_path.read_bytes())), writes via NamedTemporaryFile + atomic Path.replace(), with zero locking today. project/streamlit_app.py line 428 confirms render_sheet_editor() already wraps the call in try/except SpreadsheetError with st.error() — the contract's claim that streamlit_app.py needs no change holds. project/tests/test_send_sms.py has exactly one existing save_sheet_numbers() test using the described tempfile/openpyxl pattern; current suite is 8 tests, so 'the new suite is 11 tests' (Point 3) is arithmetically correct.\n\n3. Points 1-5 are actionable in order (implement lock creation → guaranteed cleanup → tests → doc capabilities → doc limitations) and each has concrete, mechanically checkable acceptance criteria (specific lock path format, explicit ordering relative to read_bytes()/load_workbook(), named test scenarios, exact README section edits, confirmation the other 3 limitations bullets stay untouched — verified against the actual 4-bullet 'Current limitations' section in project/README.md).\n\n4. Out of Scope is explicit and covers the realistic edge cases: no merge/versioning, no streamlit_app.py change, no retry/backoff, no stale-lock TTL recovery, no new dependency, no file outside the three named ones, and explicitly no test execution by the programmer (with a stated reason and precedent).\n\n5. No backward-compatibility break without justification: SheetSaveResult and the function's public signature are explicitly unchanged; the only behavior change (rejecting an overlapping save) is the entire justified point of the contract.\n\n6. No destructive commands and no access beyond the programmer's 'edit' permission profile: confirmed in agents/agent.py (CLAUDE_EDIT_TOOLS = Read/Grep/Glob/Edit/Write, no Bash) that the programmer genuinely cannot run the test suite; the contract correctly treats this as a manual owner follow-up, mirroring the precedent already recorded in memory/DECISIONS.md for IMPLEMENTATION_CONTRACT_0002. No file outside project/ is touched, matching AGENTS.md's project/-scoping rule (ADR-022).\n\n7. No new file/directory names are introduced that need naming-convention review; the '<workbook>.lock' sidecar path is a runtime artifact next to a network-share Excel file, not a repository path, so no gitignore/naming concern applies (P5 is not triggered).\n\n8. risk_level: checked against Tr5-base decision 7's criteria (real credentials/API keys, real external calls, native/hardware libraries, risk of landing personal/real data in git). This contract adds only a standard-library file lock around existing local/network file I/O, no new external calls, no credentials, no native libraries, and the three new tests follow the existing pattern of using synthetic fake phone numbers in a tempfile.TemporaryDirectory() (never touching the real, personal-data-bearing workbook or landing anything in git). 'standard' is appropriate; no escalation warranted.\n\n9. Minor, non-blocking observation: Point 1's acceptance criteria only pin the lock-creation ordering relative to workbook_path.read_bytes()/load_workbook(), not relative to the existing workbook_path.exists() check or the optional create_backup_copy() step, and does not specify how a non-FileExistsError (e.g. PermissionError) during lock creation should be surfaced. This is a small, reasonably-inferable implementation detail (existing code already wraps comparable errors into SpreadsheetError), not a real architectural gap per P13 — it does not require rewriting the contract, but the reviewer will check during implementation review how the programmer handled it.\n\nOverall: complete enough to implement without further clarification, consistent with existing conventions and the project's principles. Accepted as written."
    }
  ],
  "completion_notes": "",
  "implementation_review_rounds": []
}
CONTRACT-META -->
