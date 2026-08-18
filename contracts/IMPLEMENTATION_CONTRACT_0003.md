# IMPLEMENTATION_CONTRACT_0003

Status: APPROVED

---

# Workflow

- Created by: `architect`
- Reviewer (both review gates): `reviewer`
- Implementer: `programmer`
- Risk level: `standard`
- Currently with: `owner`
- Handed off to: `owner`
- Created at: `2026-08-18T15:08:37+02:00`
- Updated at: `2026-08-18T15:14:56+02:00`

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

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-18T15:12:44+02:00._

Added exclusive lock-file creation to save_sheet_numbers(): lock_path = workbook_path.with_name(f"{workbook_path.name}.lock") in the workbook's own directory. The lock is created via open(lock_path, "x") immediately after the existing workbook_path.exists() check and before any call to workbook_path.read_bytes()/load_workbook(). If FileExistsError is raised, save_sheet_numbers() raises SpreadsheetError('A save to '<path>' is already in progress. Please try again shortly.') and returns immediately — no read, load, or write of the workbook is reached (the function returns/raises before the outer try block that contains the read/modify/write logic is even entered). If lock creation succeeds, execution proceeds unchanged through the existing backup/read/modify/write logic, now nested one level inside a try/finally.

Files touched:
- `project/send_sms.py`

Tests:
- No test execution performed — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash tool, per this contract's explicit Out of Scope and the IMPLEMENTATION_CONTRACT_0002 precedent. Correctness of the new tests and the locking implementation was verified by reading and manually tracing the code paths (lock creation ordering, try/finally cleanup scope, FileExistsError rejection branch). Running the full suite (python -m unittest discover -s tests -v inside project/.venv, 11 tests total) and confirming all pass is an explicit manual follow-up for the owner.

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-18T15:14:56+02:00._

Verified in project/send_sms.py lines 422-436: lock_path = workbook_path.with_name(f"{workbook_path.name}.lock") computed in the workbook's own directory (matches 'gates.xlsx' -> 'gates.xlsx.lock' example). The exclusive open(lock_path, "x") happens at line 431, strictly before workbook_path.read_bytes()/load_workbook() at line 443 — satisfies the AC's literal ordering requirement (the pre-existing workbook_path.exists() stat check at line 426 is metadata-only, not a read, and the architecture review's round-1 note #9 already flagged this ordering nuance as non-blocking). On FileExistsError, lines 433-436 raise SpreadsheetError("A save to '{workbook_path}' is already in progress. Please try again shortly.") and return immediately — no read_bytes/load_workbook/temp-write is reached, confirmed by control flow (the raise exits the function before the second try block that contains all of that logic). When lock creation succeeds, execution falls through unchanged into the existing backup/read/modify/write logic (now nested in try/finally, but the logic itself — backup creation, load_workbook, column update loop, temp file + atomic replace, SheetSaveResult return — is unaltered).

## Point 2

SHALL: Ensure the lock file created in the previous point is always removed once the save attempt finishes, whether it succeeds or raises any exception during the read/modify/write logic, but never remove a pre-existing lock file that this call itself did not create (the 'already locked' rejection path must not delete the lock it detected).

Acceptance criteria:
- Lock-file removal after a save attempt is implemented so it runs on both the success path and every exception path raised during the read/modify/write logic (e.g. via try/finally or equivalent), covering SpreadsheetError for a missing sheet and PermissionError/OSError translated to SpreadsheetError
- After a successful call to save_sheet_numbers(), the lock file no longer exists on disk
- After a call to save_sheet_numbers() that fails for a reason unrelated to locking (e.g. the target sheet name is not found in the workbook), the lock file no longer exists on disk
- When save_sheet_numbers() rejects a call because the lock file already existed (per the previous point), that pre-existing lock file is left in place, not deleted, by the rejecting call

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-18T15:12:44+02:00._

Wrapped the entire existing read/modify/write body (backup creation, load_workbook, column update loop, temp-file write + atomic replace, and the SheetSaveResult return) in a try/finally where the finally clause unconditionally calls lock_path.unlink(missing_ok=True). This finally is only reached after the lock was actually created by this call (the rejection branch on FileExistsError raises before this try block is entered, so a pre-existing lock detected by another call is never touched by the rejecting call). Cleanup therefore runs identically on the success return, on SpreadsheetError raised for a missing sheet, and on PermissionError/OSError translated to SpreadsheetError during the temp-file save/replace.

Files touched:
- `project/send_sms.py`

Tests:
- No test execution performed — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash tool, per this contract's explicit Out of Scope and the IMPLEMENTATION_CONTRACT_0002 precedent. Correctness of the new tests and the locking implementation was verified by reading and manually tracing the code paths (lock creation ordering, try/finally cleanup scope, FileExistsError rejection branch). Running the full suite (python -m unittest discover -s tests -v inside project/.venv, 11 tests total) and confirming all pass is an explicit manual follow-up for the owner.

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-18T15:14:56+02:00._

Verified the outer try (send_sms.py line 438) covers backup creation, load_workbook, worksheet lookup, the column update loop, the temp-file save/replace, and the SheetSaveResult return, with a matching finally at line 491-492 that unconditionally calls lock_path.unlink(missing_ok=True). This finally runs on the success return path, on SpreadsheetError raised for a missing sheet (worksheet lookup KeyError at line 451-452), and on PermissionError/OSError translated to SpreadsheetError during the temp-file save/replace (lines 472-477) — all propagate up through the same try, hitting the same finally. The rejection branch (FileExistsError on lock creation, lines 433-436) raises from inside the earlier, separate try/except (lines 430-436), before the try/finally at 438/491 is ever entered — so a pre-existing lock detected by a rejecting call is structurally never unlinked by that call. Confirmed directly by the new test test_save_sheet_numbers_rejects_when_lock_file_present, which asserts the pre-created lock file still exists after the rejected call.

## Point 3

SHALL: Add three new unit tests to project/tests/test_send_sms.py covering the new locking behavior, following the existing tempfile-based workbook/config fixture pattern used by test_save_sheet_numbers_normalizes_and_preserves_other_columns.

Acceptance criteria:
- Three new test methods are added, distinctly named for their scenario (e.g. test_save_sheet_numbers_removes_lock_after_success, test_save_sheet_numbers_rejects_when_lock_file_present, test_save_sheet_numbers_removes_lock_after_unrelated_failure)
- Each new test uses the existing tempfile.TemporaryDirectory()-based real-workbook/config fixture pattern, not a mocked filesystem
- Reading the 'removes_lock_after_success' test confirms it performs a normal save and then asserts the '<workbook>.lock' file does not exist afterward
- Reading the 'rejects_when_lock_file_present' test confirms it pre-creates the '<workbook>.lock' file, calls save_sheet_numbers(), asserts a SpreadsheetError is raised, and asserts the workbook file's bytes on disk are unchanged from before the call
- Reading the 'removes_lock_after_unrelated_failure' test confirms it triggers an existing unrelated failure path (e.g. a sheet_name that does not exist in the workbook), asserts a SpreadsheetError is raised, and asserts the '<workbook>.lock' file does not exist afterward
- Actually executing the full test suite (11 tests total after this addition) and confirming all pass is explicitly left as a manual follow-up for the owner, per this contract's Out of Scope, since the programmer has no Bash access to run it

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-18T15:12:44+02:00._

Added three new test methods to project/tests/test_send_sms.py, each using the existing tempfile.TemporaryDirectory()-based real openpyxl workbook + real config.toml fixture pattern (no filesystem mocking): (1) test_save_sheet_numbers_removes_lock_after_success — performs a normal save, then asserts '<workbook>.lock' does not exist afterward; (2) test_save_sheet_numbers_rejects_when_lock_file_present — pre-creates the '.lock' file, calls save_sheet_numbers(), asserts SpreadsheetError is raised, asserts the workbook's on-disk bytes are unchanged from before the call, and additionally asserts the pre-existing lock file is still present (tracing point 2's non-deletion requirement); (3) test_save_sheet_numbers_removes_lock_after_unrelated_failure — calls save_sheet_numbers() with a sheet_name ('Nonexistent Sheet') absent from the workbook, asserts SpreadsheetError is raised, and asserts the '.lock' file does not exist afterward. Also added SpreadsheetError to the module's `from send_sms import (...)` block since the new tests need to assertRaises against it. I traced each test's logic against the point 1/point 2 implementation by hand (open('x') semantics, unlink(missing_ok=True) placement, and the exact lock-path/'x' arguments used by save_sheet_numbers()) and confirmed they align; I could not execute the suite myself since the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash tool. Running the full suite (11 tests total) and confirming all pass is left as the explicit manual owner follow-up called for in this contract's Out of Scope.

Files touched:
- `project/tests/test_send_sms.py`

Tests:
- No test execution performed — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash tool, per this contract's explicit Out of Scope and the IMPLEMENTATION_CONTRACT_0002 precedent. Correctness of the new tests and the locking implementation was verified by reading and manually tracing the code paths (lock creation ordering, try/finally cleanup scope, FileExistsError rejection branch). Running the full suite (python -m unittest discover -s tests -v inside project/.venv, 11 tests total) and confirming all pass is an explicit manual follow-up for the owner.

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-18T15:14:56+02:00._

Three new, distinctly named test methods added to project/tests/test_send_sms.py (test_save_sheet_numbers_removes_lock_after_success, test_save_sheet_numbers_rejects_when_lock_file_present, test_save_sheet_numbers_removes_lock_after_unrelated_failure), each using the same tempfile.TemporaryDirectory()-based real openpyxl workbook + real config.toml fixture pattern as the existing test (no mocked filesystem). 'removes_lock_after_success' performs a normal save then asserts lock_path.exists() is False. 'rejects_when_lock_file_present' pre-creates the lock file via write_text, calls save_sheet_numbers(), asserts SpreadsheetError is raised, asserts workbook_path.read_bytes() is byte-identical to the pre-call snapshot, and additionally asserts the pre-existing lock file is still present. 'removes_lock_after_unrelated_failure' calls save_sheet_numbers() with sheet_name='Nonexistent Sheet' (absent from the workbook), asserts SpreadsheetError is raised, and asserts the lock file does not exist afterward. SpreadsheetError was correctly added to the test file's import block. Counting the test file confirms 8 pre-existing + 3 new = 11 test methods, matching the contract's stated total; actual execution remains an explicit manual owner follow-up per this contract's Out of Scope, which is consistent with the programmer's 'edit'-only permission profile (no Bash tool).

## Point 4

SHALL: Add a bullet to the 'Current capabilities (v0.1)' section of project/README.md describing that save_sheet_numbers() now detects and rejects an overlapping concurrent save via a sidecar lock file, instead of silently allowing one save to overwrite another.

Acceptance criteria:
- The 'Current capabilities (v0.1)' section contains a new bullet stating that concurrent saves to the shared Excel workbook are detected and safely rejected (not silently overwritten), naming the mechanism as a sidecar lock file
- The new bullet does not claim to solve stale-lock recovery or any form of multi-writer merge
- No existing bullet in 'Current capabilities (v0.1)' is removed or altered by this point

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-18T15:12:44+02:00._

Added a new bullet directly under the existing send_sms.py bullet in the 'Current capabilities (v0.1)' section of project/README.md stating that concurrent saves to the shared Excel workbook are now detected and safely rejected (not silently overwritten) via a sidecar '<workbook>.lock' file created before the workbook is read. The bullet makes no claim about stale-lock recovery or multi-writer merge. No existing bullet in that section was removed or altered.

Files touched:
- `project/README.md`

Tests:
- No test execution performed — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash tool, per this contract's explicit Out of Scope and the IMPLEMENTATION_CONTRACT_0002 precedent. Correctness of the new tests and the locking implementation was verified by reading and manually tracing the code paths (lock creation ordering, try/finally cleanup scope, FileExistsError rejection branch). Running the full suite (python -m unittest discover -s tests -v inside project/.venv, 11 tests total) and confirming all pass is an explicit manual follow-up for the owner.

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-18T15:14:56+02:00._

project/README.md's 'Current capabilities (v0.1)' section (lines 25-29) now contains a new bullet immediately after the send_sms.py bullet, stating that concurrent saves are 'detected and safely rejected, not silently overwritten' via a sidecar '<workbook>.lock' file created before the workbook is read, and that an overlapping save 'fails with a clear error instead of racing the first one.' The bullet makes no claim about stale-lock recovery or multi-writer merge. All other bullets in the section (send_sms.py, main.py, streamlit_app.py, tests/test_send_sms.py, config.example.toml) are present and textually unchanged from before this contract.

## Point 5

SHALL: Update the 'Current limitations' section of project/README.md: remove the existing bullet stating there is no file locking for concurrent Excel writes, and replace it with a narrower bullet stating that a lock file left behind by a process that crashes mid-save is not automatically cleared (no staleness/TTL recovery), so such a lock would need manual removal.

Acceptance criteria:
- The 'Current limitations' section no longer contains the original 'no file locking for concurrent writes to the shared Excel workbook' bullet
- The 'Current limitations' section contains a new bullet specifically about stale-lock recovery not being automatic, as described above
- The other three limitations bullets (missing CLI/UI test coverage, no CLI --timeout parity, the single global phone-column-index assumption) remain present and unaltered

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-18T15:12:44+02:00._

In the 'Current limitations' section of project/README.md, replaced the original bullet ('No file locking protects concurrent writes to the shared Excel workbook when multiple users save through the Streamlit editor at the same time.') with a narrower bullet stating a '<workbook>.lock' file left behind by a process that crashes mid-save is not automatically cleared (no staleness/TTL recovery) and would need manual removal. The other three limitations bullets (missing CLI/UI test coverage, no CLI --timeout parity, single global phone-column-index assumption) were left present and unaltered, verified by re-reading the section after the edit. Note (not required by this point's acceptance criteria, so left as-is per contract scope, flagged here for visibility): the 'tests/test_send_sms.py' bullet in 'Current capabilities' still says 'the full suite (8 tests)' and the 'Planned evolution' section still lists 'concurrent-write protection' among limitations still to resolve — both are now stale given the 3 new tests and this contract's resolution, but updating them was not requested by any point of this contract (only the two named sections/bullets were in scope), so I did not touch them to avoid scope creep beyond what was contracted.

Files touched:
- `project/README.md`

Tests:
- No test execution performed — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash tool, per this contract's explicit Out of Scope and the IMPLEMENTATION_CONTRACT_0002 precedent. Correctness of the new tests and the locking implementation was verified by reading and manually tracing the code paths (lock creation ordering, try/finally cleanup scope, FileExistsError rejection branch). Running the full suite (python -m unittest discover -s tests -v inside project/.venv, 11 tests total) and confirming all pass is an explicit manual follow-up for the owner.

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-18T15:14:56+02:00._

project/README.md's 'Current limitations' section (lines 69-76) no longer contains the original 'no file locking for concurrent writes' bullet; it has been replaced with a new bullet (lines 71-73) stating a '<workbook>.lock' file left behind by a crashed process is not automatically cleared (no staleness/TTL recovery) and would need manual removal — matching the point's required wording exactly. The other three limitations bullets (missing CLI/UI test coverage, no CLI --timeout parity, single global phone-column-index assumption) remain present and unaltered, confirmed by direct comparison. Minor, non-blocking observation (already flagged by the programmer in the completion note for transparency, not silently hidden): the 'tests/test_send_sms.py (8 tests)' capabilities bullet and the 'Planned evolution' section's mention of 'concurrent-write protection' as an unresolved limitation are now stale given this contract's resolution and the new 11-test suite, but neither was named by this contract's points (only two specific bullets were in scope), so leaving them untouched is the correct call under P13/Out-of-Scope discipline rather than a defect — worth a future light-touch fix, not a reason to request changes here.

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

Implemented atomic file-based lock detection in save_sheet_numbers() (project/send_sms.py) so an overlapping save fails loudly with SpreadsheetError instead of silently racing another writer, with guaranteed lock cleanup on every path except the rejection path itself. Added three new unit tests to project/tests/test_send_sms.py following the existing tempfile/openpyxl fixture pattern, and updated project/README.md to move the resolved concurrent-write limitation into 'Current capabilities' and add the narrower residual stale-lock limitation. project/streamlit_app.py was verified (not modified) — its existing try/except SpreadsheetError/st.error() path already surfaces the new rejection to users. The programmer has no Bash access (permission_profile 'edit'), so the new/full test suite (11 tests) was verified by reading and tracing logic against the implementation rather than executed; running it is a manual follow-up for the owner, per the contract's Out of Scope and the IMPLEMENTATION_CONTRACT_0002 precedent.

---

# Implementation Review

### Round 1 — 2026-08-18T15:14:56+02:00 — Verdict: APPROVED — Reviewer: `reviewer`

All five points are correctly and completely implemented as accepted in the architecture review. project/send_sms.py's save_sheet_numbers() now creates an exclusive sidecar '<workbook>.lock' file (open(lock_path, "x")) before any read_bytes()/load_workbook() call, raises SpreadsheetError with a clear 'already in progress' message on FileExistsError without touching the workbook, and guarantees lock cleanup via a try/finally wrapped around the entire read/modify/write body — while the rejection branch (which raises before that try/finally is entered) never deletes a lock it did not create. Three new tests in project/tests/test_send_sms.py follow the existing tempfile/openpyxl real-fixture pattern and correctly assert success-path cleanup, rejection-with-unchanged-bytes-and-preserved-lock, and cleanup-after-an-unrelated-failure (nonexistent sheet). project/README.md was updated exactly as specified: a new 'Current capabilities' bullet describing the lock mechanism (making no claim about stale-lock recovery or merge), and the old 'no file locking' limitation bullet replaced with the narrower stale-lock bullet, leaving the other three limitations bullets untouched. project/streamlit_app.py was verified, not modified, and its existing try/except SpreadsheetError/st.error() path already surfaces the new rejection. No new third-party dependency, no public signature/return-type change, no file touched outside the three named files.

Out of Scope check: OK — Discovery diff listed 5 changed paths. project/send_sms.py, project/tests/test_send_sms.py, and project/README.md are exactly the three files this contract's Outputs/Out-of-Scope sections permit, and their content changes map precisely to points 1-5 with no unrelated edits found by reading the full files. The other two changed paths — agents/architect/WORKING_STATE.md and agents/programmer/runtime/session.log — are framework-generated artifacts, not manual programmer edits beyond the contract: WORKING_STATE.md's own header states it is 'Generated automatically from the live contract queue on every state change... do not edit by hand,' and its content is just the queue's current status line for this contract; session.log is an append-only tool-invocation log whose tail (Read/Edit calls on send_sms.py, test_send_sms.py x2, README.md x2 around 15:10-15:12) exactly matches the actual edits made and nothing more. Additionally verified project/streamlit_app.py was read but not modified (not in the diff list, and its existing try/except SpreadsheetError/st.error() block at lines 420-429 already correctly surfaces the new rejection, confirming the contract's claim it needed no change) and confirmed no new dependency or gitignore change was introduced (the lock file is a runtime sidecar next to the network-share workbook, outside the repo, so P5 does not apply). No scope creep found.

---

# Lessons Learned

_Not filled in._

---

<!-- CONTRACT-META
{
  "number": 3,
  "title": "Detect and reject concurrent writes to the shared Excel workbook",
  "status": "APPROVED",
  "created_by": "architect",
  "assigned_to": "owner",
  "handoff_to": "owner",
  "created_at": "2026-08-18T15:08:37+02:00",
  "updated_at": "2026-08-18T15:14:56+02:00",
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
      "programmer_note": "Added exclusive lock-file creation to save_sheet_numbers(): lock_path = workbook_path.with_name(f\"{workbook_path.name}.lock\") in the workbook's own directory. The lock is created via open(lock_path, \"x\") immediately after the existing workbook_path.exists() check and before any call to workbook_path.read_bytes()/load_workbook(). If FileExistsError is raised, save_sheet_numbers() raises SpreadsheetError('A save to '<path>' is already in progress. Please try again shortly.') and returns immediately — no read, load, or write of the workbook is reached (the function returns/raises before the outer try block that contains the read/modify/write logic is even entered). If lock creation succeeds, execution proceeds unchanged through the existing backup/read/modify/write logic, now nested one level inside a try/finally.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T15:12:44+02:00",
      "programmer_files": [
        "project/send_sms.py"
      ],
      "programmer_tests": [
        "No test execution performed — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash tool, per this contract's explicit Out of Scope and the IMPLEMENTATION_CONTRACT_0002 precedent. Correctness of the new tests and the locking implementation was verified by reading and manually tracing the code paths (lock creation ordering, try/finally cleanup scope, FileExistsError rejection branch). Running the full suite (python -m unittest discover -s tests -v inside project/.venv, 11 tests total) and confirming all pass is an explicit manual follow-up for the owner."
      ],
      "reviewer_note": "Verified in project/send_sms.py lines 422-436: lock_path = workbook_path.with_name(f\"{workbook_path.name}.lock\") computed in the workbook's own directory (matches 'gates.xlsx' -> 'gates.xlsx.lock' example). The exclusive open(lock_path, \"x\") happens at line 431, strictly before workbook_path.read_bytes()/load_workbook() at line 443 — satisfies the AC's literal ordering requirement (the pre-existing workbook_path.exists() stat check at line 426 is metadata-only, not a read, and the architecture review's round-1 note #9 already flagged this ordering nuance as non-blocking). On FileExistsError, lines 433-436 raise SpreadsheetError(\"A save to '{workbook_path}' is already in progress. Please try again shortly.\") and return immediately — no read_bytes/load_workbook/temp-write is reached, confirmed by control flow (the raise exits the function before the second try block that contains all of that logic). When lock creation succeeds, execution falls through unchanged into the existing backup/read/modify/write logic (now nested in try/finally, but the logic itself — backup creation, load_workbook, column update loop, temp file + atomic replace, SheetSaveResult return — is unaltered).",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-18T15:14:56+02:00",
      "status": "APPROVED"
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
      "programmer_note": "Wrapped the entire existing read/modify/write body (backup creation, load_workbook, column update loop, temp-file write + atomic replace, and the SheetSaveResult return) in a try/finally where the finally clause unconditionally calls lock_path.unlink(missing_ok=True). This finally is only reached after the lock was actually created by this call (the rejection branch on FileExistsError raises before this try block is entered, so a pre-existing lock detected by another call is never touched by the rejecting call). Cleanup therefore runs identically on the success return, on SpreadsheetError raised for a missing sheet, and on PermissionError/OSError translated to SpreadsheetError during the temp-file save/replace.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T15:12:44+02:00",
      "programmer_files": [
        "project/send_sms.py"
      ],
      "programmer_tests": [
        "No test execution performed — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash tool, per this contract's explicit Out of Scope and the IMPLEMENTATION_CONTRACT_0002 precedent. Correctness of the new tests and the locking implementation was verified by reading and manually tracing the code paths (lock creation ordering, try/finally cleanup scope, FileExistsError rejection branch). Running the full suite (python -m unittest discover -s tests -v inside project/.venv, 11 tests total) and confirming all pass is an explicit manual follow-up for the owner."
      ],
      "reviewer_note": "Verified the outer try (send_sms.py line 438) covers backup creation, load_workbook, worksheet lookup, the column update loop, the temp-file save/replace, and the SheetSaveResult return, with a matching finally at line 491-492 that unconditionally calls lock_path.unlink(missing_ok=True). This finally runs on the success return path, on SpreadsheetError raised for a missing sheet (worksheet lookup KeyError at line 451-452), and on PermissionError/OSError translated to SpreadsheetError during the temp-file save/replace (lines 472-477) — all propagate up through the same try, hitting the same finally. The rejection branch (FileExistsError on lock creation, lines 433-436) raises from inside the earlier, separate try/except (lines 430-436), before the try/finally at 438/491 is ever entered — so a pre-existing lock detected by a rejecting call is structurally never unlinked by that call. Confirmed directly by the new test test_save_sheet_numbers_rejects_when_lock_file_present, which asserts the pre-created lock file still exists after the rejected call.",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-18T15:14:56+02:00",
      "status": "APPROVED"
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
      "programmer_note": "Added three new test methods to project/tests/test_send_sms.py, each using the existing tempfile.TemporaryDirectory()-based real openpyxl workbook + real config.toml fixture pattern (no filesystem mocking): (1) test_save_sheet_numbers_removes_lock_after_success — performs a normal save, then asserts '<workbook>.lock' does not exist afterward; (2) test_save_sheet_numbers_rejects_when_lock_file_present — pre-creates the '.lock' file, calls save_sheet_numbers(), asserts SpreadsheetError is raised, asserts the workbook's on-disk bytes are unchanged from before the call, and additionally asserts the pre-existing lock file is still present (tracing point 2's non-deletion requirement); (3) test_save_sheet_numbers_removes_lock_after_unrelated_failure — calls save_sheet_numbers() with a sheet_name ('Nonexistent Sheet') absent from the workbook, asserts SpreadsheetError is raised, and asserts the '.lock' file does not exist afterward. Also added SpreadsheetError to the module's `from send_sms import (...)` block since the new tests need to assertRaises against it. I traced each test's logic against the point 1/point 2 implementation by hand (open('x') semantics, unlink(missing_ok=True) placement, and the exact lock-path/'x' arguments used by save_sheet_numbers()) and confirmed they align; I could not execute the suite myself since the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash tool. Running the full suite (11 tests total) and confirming all pass is left as the explicit manual owner follow-up called for in this contract's Out of Scope.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T15:12:44+02:00",
      "programmer_files": [
        "project/tests/test_send_sms.py"
      ],
      "programmer_tests": [
        "No test execution performed — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash tool, per this contract's explicit Out of Scope and the IMPLEMENTATION_CONTRACT_0002 precedent. Correctness of the new tests and the locking implementation was verified by reading and manually tracing the code paths (lock creation ordering, try/finally cleanup scope, FileExistsError rejection branch). Running the full suite (python -m unittest discover -s tests -v inside project/.venv, 11 tests total) and confirming all pass is an explicit manual follow-up for the owner."
      ],
      "reviewer_note": "Three new, distinctly named test methods added to project/tests/test_send_sms.py (test_save_sheet_numbers_removes_lock_after_success, test_save_sheet_numbers_rejects_when_lock_file_present, test_save_sheet_numbers_removes_lock_after_unrelated_failure), each using the same tempfile.TemporaryDirectory()-based real openpyxl workbook + real config.toml fixture pattern as the existing test (no mocked filesystem). 'removes_lock_after_success' performs a normal save then asserts lock_path.exists() is False. 'rejects_when_lock_file_present' pre-creates the lock file via write_text, calls save_sheet_numbers(), asserts SpreadsheetError is raised, asserts workbook_path.read_bytes() is byte-identical to the pre-call snapshot, and additionally asserts the pre-existing lock file is still present. 'removes_lock_after_unrelated_failure' calls save_sheet_numbers() with sheet_name='Nonexistent Sheet' (absent from the workbook), asserts SpreadsheetError is raised, and asserts the lock file does not exist afterward. SpreadsheetError was correctly added to the test file's import block. Counting the test file confirms 8 pre-existing + 3 new = 11 test methods, matching the contract's stated total; actual execution remains an explicit manual owner follow-up per this contract's Out of Scope, which is consistent with the programmer's 'edit'-only permission profile (no Bash tool).",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-18T15:14:56+02:00",
      "status": "APPROVED"
    },
    {
      "number": 4,
      "assignment": "Add a bullet to the 'Current capabilities (v0.1)' section of project/README.md describing that save_sheet_numbers() now detects and rejects an overlapping concurrent save via a sidecar lock file, instead of silently allowing one save to overwrite another.",
      "acceptance_criteria": [
        "The 'Current capabilities (v0.1)' section contains a new bullet stating that concurrent saves to the shared Excel workbook are detected and safely rejected (not silently overwritten), naming the mechanism as a sidecar lock file",
        "The new bullet does not claim to solve stale-lock recovery or any form of multi-writer merge",
        "No existing bullet in 'Current capabilities (v0.1)' is removed or altered by this point"
      ],
      "programmer_note": "Added a new bullet directly under the existing send_sms.py bullet in the 'Current capabilities (v0.1)' section of project/README.md stating that concurrent saves to the shared Excel workbook are now detected and safely rejected (not silently overwritten) via a sidecar '<workbook>.lock' file created before the workbook is read. The bullet makes no claim about stale-lock recovery or multi-writer merge. No existing bullet in that section was removed or altered.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T15:12:44+02:00",
      "programmer_files": [
        "project/README.md"
      ],
      "programmer_tests": [
        "No test execution performed — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash tool, per this contract's explicit Out of Scope and the IMPLEMENTATION_CONTRACT_0002 precedent. Correctness of the new tests and the locking implementation was verified by reading and manually tracing the code paths (lock creation ordering, try/finally cleanup scope, FileExistsError rejection branch). Running the full suite (python -m unittest discover -s tests -v inside project/.venv, 11 tests total) and confirming all pass is an explicit manual follow-up for the owner."
      ],
      "reviewer_note": "project/README.md's 'Current capabilities (v0.1)' section (lines 25-29) now contains a new bullet immediately after the send_sms.py bullet, stating that concurrent saves are 'detected and safely rejected, not silently overwritten' via a sidecar '<workbook>.lock' file created before the workbook is read, and that an overlapping save 'fails with a clear error instead of racing the first one.' The bullet makes no claim about stale-lock recovery or multi-writer merge. All other bullets in the section (send_sms.py, main.py, streamlit_app.py, tests/test_send_sms.py, config.example.toml) are present and textually unchanged from before this contract.",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-18T15:14:56+02:00",
      "status": "APPROVED"
    },
    {
      "number": 5,
      "assignment": "Update the 'Current limitations' section of project/README.md: remove the existing bullet stating there is no file locking for concurrent Excel writes, and replace it with a narrower bullet stating that a lock file left behind by a process that crashes mid-save is not automatically cleared (no staleness/TTL recovery), so such a lock would need manual removal.",
      "acceptance_criteria": [
        "The 'Current limitations' section no longer contains the original 'no file locking for concurrent writes to the shared Excel workbook' bullet",
        "The 'Current limitations' section contains a new bullet specifically about stale-lock recovery not being automatic, as described above",
        "The other three limitations bullets (missing CLI/UI test coverage, no CLI --timeout parity, the single global phone-column-index assumption) remain present and unaltered"
      ],
      "programmer_note": "In the 'Current limitations' section of project/README.md, replaced the original bullet ('No file locking protects concurrent writes to the shared Excel workbook when multiple users save through the Streamlit editor at the same time.') with a narrower bullet stating a '<workbook>.lock' file left behind by a process that crashes mid-save is not automatically cleared (no staleness/TTL recovery) and would need manual removal. The other three limitations bullets (missing CLI/UI test coverage, no CLI --timeout parity, single global phone-column-index assumption) were left present and unaltered, verified by re-reading the section after the edit. Note (not required by this point's acceptance criteria, so left as-is per contract scope, flagged here for visibility): the 'tests/test_send_sms.py' bullet in 'Current capabilities' still says 'the full suite (8 tests)' and the 'Planned evolution' section still lists 'concurrent-write protection' among limitations still to resolve — both are now stale given the 3 new tests and this contract's resolution, but updating them was not requested by any point of this contract (only the two named sections/bullets were in scope), so I did not touch them to avoid scope creep beyond what was contracted.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T15:12:44+02:00",
      "programmer_files": [
        "project/README.md"
      ],
      "programmer_tests": [
        "No test execution performed — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash tool, per this contract's explicit Out of Scope and the IMPLEMENTATION_CONTRACT_0002 precedent. Correctness of the new tests and the locking implementation was verified by reading and manually tracing the code paths (lock creation ordering, try/finally cleanup scope, FileExistsError rejection branch). Running the full suite (python -m unittest discover -s tests -v inside project/.venv, 11 tests total) and confirming all pass is an explicit manual follow-up for the owner."
      ],
      "reviewer_note": "project/README.md's 'Current limitations' section (lines 69-76) no longer contains the original 'no file locking for concurrent writes' bullet; it has been replaced with a new bullet (lines 71-73) stating a '<workbook>.lock' file left behind by a crashed process is not automatically cleared (no staleness/TTL recovery) and would need manual removal — matching the point's required wording exactly. The other three limitations bullets (missing CLI/UI test coverage, no CLI --timeout parity, single global phone-column-index assumption) remain present and unaltered, confirmed by direct comparison. Minor, non-blocking observation (already flagged by the programmer in the completion note for transparency, not silently hidden): the 'tests/test_send_sms.py (8 tests)' capabilities bullet and the 'Planned evolution' section's mention of 'concurrent-write protection' as an unresolved limitation are now stale given this contract's resolution and the new 11-test suite, but neither was named by this contract's points (only two specific bullets were in scope), so leaving them untouched is the correct call under P13/Out-of-Scope discipline rather than a defect — worth a future light-touch fix, not a reason to request changes here.",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-18T15:14:56+02:00",
      "status": "APPROVED"
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
  "completion_notes": "Implemented atomic file-based lock detection in save_sheet_numbers() (project/send_sms.py) so an overlapping save fails loudly with SpreadsheetError instead of silently racing another writer, with guaranteed lock cleanup on every path except the rejection path itself. Added three new unit tests to project/tests/test_send_sms.py following the existing tempfile/openpyxl fixture pattern, and updated project/README.md to move the resolved concurrent-write limitation into 'Current capabilities' and add the narrower residual stale-lock limitation. project/streamlit_app.py was verified (not modified) — its existing try/except SpreadsheetError/st.error() path already surfaces the new rejection to users. The programmer has no Bash access (permission_profile 'edit'), so the new/full test suite (11 tests) was verified by reading and tracing logic against the implementation rather than executed; running it is a manual follow-up for the owner, per the contract's Out of Scope and the IMPLEMENTATION_CONTRACT_0002 precedent.",
  "implementation_review_rounds": [
    {
      "round": 1,
      "date": "2026-08-18T15:14:56+02:00",
      "verdict": "APPROVED",
      "reviewer": "reviewer",
      "summary": "All five points are correctly and completely implemented as accepted in the architecture review. project/send_sms.py's save_sheet_numbers() now creates an exclusive sidecar '<workbook>.lock' file (open(lock_path, \"x\")) before any read_bytes()/load_workbook() call, raises SpreadsheetError with a clear 'already in progress' message on FileExistsError without touching the workbook, and guarantees lock cleanup via a try/finally wrapped around the entire read/modify/write body — while the rejection branch (which raises before that try/finally is entered) never deletes a lock it did not create. Three new tests in project/tests/test_send_sms.py follow the existing tempfile/openpyxl real-fixture pattern and correctly assert success-path cleanup, rejection-with-unchanged-bytes-and-preserved-lock, and cleanup-after-an-unrelated-failure (nonexistent sheet). project/README.md was updated exactly as specified: a new 'Current capabilities' bullet describing the lock mechanism (making no claim about stale-lock recovery or merge), and the old 'no file locking' limitation bullet replaced with the narrower stale-lock bullet, leaving the other three limitations bullets untouched. project/streamlit_app.py was verified, not modified, and its existing try/except SpreadsheetError/st.error() path already surfaces the new rejection. No new third-party dependency, no public signature/return-type change, no file touched outside the three named files.",
      "out_of_scope_ok": true,
      "out_of_scope_findings": "Discovery diff listed 5 changed paths. project/send_sms.py, project/tests/test_send_sms.py, and project/README.md are exactly the three files this contract's Outputs/Out-of-Scope sections permit, and their content changes map precisely to points 1-5 with no unrelated edits found by reading the full files. The other two changed paths — agents/architect/WORKING_STATE.md and agents/programmer/runtime/session.log — are framework-generated artifacts, not manual programmer edits beyond the contract: WORKING_STATE.md's own header states it is 'Generated automatically from the live contract queue on every state change... do not edit by hand,' and its content is just the queue's current status line for this contract; session.log is an append-only tool-invocation log whose tail (Read/Edit calls on send_sms.py, test_send_sms.py x2, README.md x2 around 15:10-15:12) exactly matches the actual edits made and nothing more. Additionally verified project/streamlit_app.py was read but not modified (not in the diff list, and its existing try/except SpreadsheetError/st.error() block at lines 420-429 already correctly surfaces the new rejection, confirming the contract's claim it needed no change) and confirmed no new dependency or gitignore change was introduced (the lock file is a runtime sidecar next to the network-share workbook, outside the repo, so P5 does not apply). No scope creep found.",
      "reviews": [
        {
          "point": 1,
          "status": "APPROVED",
          "review": "Verified in project/send_sms.py lines 422-436: lock_path = workbook_path.with_name(f\"{workbook_path.name}.lock\") computed in the workbook's own directory (matches 'gates.xlsx' -> 'gates.xlsx.lock' example). The exclusive open(lock_path, \"x\") happens at line 431, strictly before workbook_path.read_bytes()/load_workbook() at line 443 — satisfies the AC's literal ordering requirement (the pre-existing workbook_path.exists() stat check at line 426 is metadata-only, not a read, and the architecture review's round-1 note #9 already flagged this ordering nuance as non-blocking). On FileExistsError, lines 433-436 raise SpreadsheetError(\"A save to '{workbook_path}' is already in progress. Please try again shortly.\") and return immediately — no read_bytes/load_workbook/temp-write is reached, confirmed by control flow (the raise exits the function before the second try block that contains all of that logic). When lock creation succeeds, execution falls through unchanged into the existing backup/read/modify/write logic (now nested in try/finally, but the logic itself — backup creation, load_workbook, column update loop, temp file + atomic replace, SheetSaveResult return — is unaltered)."
        },
        {
          "point": 2,
          "status": "APPROVED",
          "review": "Verified the outer try (send_sms.py line 438) covers backup creation, load_workbook, worksheet lookup, the column update loop, the temp-file save/replace, and the SheetSaveResult return, with a matching finally at line 491-492 that unconditionally calls lock_path.unlink(missing_ok=True). This finally runs on the success return path, on SpreadsheetError raised for a missing sheet (worksheet lookup KeyError at line 451-452), and on PermissionError/OSError translated to SpreadsheetError during the temp-file save/replace (lines 472-477) — all propagate up through the same try, hitting the same finally. The rejection branch (FileExistsError on lock creation, lines 433-436) raises from inside the earlier, separate try/except (lines 430-436), before the try/finally at 438/491 is ever entered — so a pre-existing lock detected by a rejecting call is structurally never unlinked by that call. Confirmed directly by the new test test_save_sheet_numbers_rejects_when_lock_file_present, which asserts the pre-created lock file still exists after the rejected call."
        },
        {
          "point": 3,
          "status": "APPROVED",
          "review": "Three new, distinctly named test methods added to project/tests/test_send_sms.py (test_save_sheet_numbers_removes_lock_after_success, test_save_sheet_numbers_rejects_when_lock_file_present, test_save_sheet_numbers_removes_lock_after_unrelated_failure), each using the same tempfile.TemporaryDirectory()-based real openpyxl workbook + real config.toml fixture pattern as the existing test (no mocked filesystem). 'removes_lock_after_success' performs a normal save then asserts lock_path.exists() is False. 'rejects_when_lock_file_present' pre-creates the lock file via write_text, calls save_sheet_numbers(), asserts SpreadsheetError is raised, asserts workbook_path.read_bytes() is byte-identical to the pre-call snapshot, and additionally asserts the pre-existing lock file is still present. 'removes_lock_after_unrelated_failure' calls save_sheet_numbers() with sheet_name='Nonexistent Sheet' (absent from the workbook), asserts SpreadsheetError is raised, and asserts the lock file does not exist afterward. SpreadsheetError was correctly added to the test file's import block. Counting the test file confirms 8 pre-existing + 3 new = 11 test methods, matching the contract's stated total; actual execution remains an explicit manual owner follow-up per this contract's Out of Scope, which is consistent with the programmer's 'edit'-only permission profile (no Bash tool)."
        },
        {
          "point": 4,
          "status": "APPROVED",
          "review": "project/README.md's 'Current capabilities (v0.1)' section (lines 25-29) now contains a new bullet immediately after the send_sms.py bullet, stating that concurrent saves are 'detected and safely rejected, not silently overwritten' via a sidecar '<workbook>.lock' file created before the workbook is read, and that an overlapping save 'fails with a clear error instead of racing the first one.' The bullet makes no claim about stale-lock recovery or multi-writer merge. All other bullets in the section (send_sms.py, main.py, streamlit_app.py, tests/test_send_sms.py, config.example.toml) are present and textually unchanged from before this contract."
        },
        {
          "point": 5,
          "status": "APPROVED",
          "review": "project/README.md's 'Current limitations' section (lines 69-76) no longer contains the original 'no file locking for concurrent writes' bullet; it has been replaced with a new bullet (lines 71-73) stating a '<workbook>.lock' file left behind by a crashed process is not automatically cleared (no staleness/TTL recovery) and would need manual removal — matching the point's required wording exactly. The other three limitations bullets (missing CLI/UI test coverage, no CLI --timeout parity, single global phone-column-index assumption) remain present and unaltered, confirmed by direct comparison. Minor, non-blocking observation (already flagged by the programmer in the completion note for transparency, not silently hidden): the 'tests/test_send_sms.py (8 tests)' capabilities bullet and the 'Planned evolution' section's mention of 'concurrent-write protection' as an unresolved limitation are now stale given this contract's resolution and the new 11-test suite, but neither was named by this contract's points (only two specific bullets were in scope), so leaving them untouched is the correct call under P13/Out-of-Scope discipline rather than a defect — worth a future light-touch fix, not a reason to request changes here."
        }
      ]
    }
  ]
}
CONTRACT-META -->
