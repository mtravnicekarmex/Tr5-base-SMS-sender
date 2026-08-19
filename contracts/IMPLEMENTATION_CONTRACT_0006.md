# IMPLEMENTATION_CONTRACT_0006

Status: APPROVED

---

# Workflow

- Created by: `architect`
- Reviewer (both review gates): `reviewer`
- Implementer: `programmer`
- Risk level: `standard`
- Currently with: `owner`
- Handed off to: `owner`
- Created at: `2026-08-19T14:41:41+02:00`
- Updated at: `2026-08-19T14:49:48+02:00`

---

# Title

Add automated test coverage for main.py and streamlit_app.py's pure helpers

---

# Purpose

project/main.py (the CLI) and project/streamlit_app.py (the web UI) are the two user-facing surfaces of the SMS gateway tool and currently have zero automated test coverage, unlike project/send_sms.py's core logic (13 tests). A regression in CLI argument parsing, dispatch, or exit-code logic, or in the Streamlit app's data-transformation helpers, would only be caught by manual testing today. This closes the last remaining item from the architect's original code review queue by adding real, targeted coverage wherever it is safely and deterministically achievable without a live network, a live Excel file, or a running Streamlit server.

---

# Intent

This adds test coverage where it is safely and deterministically achievable: main.py's argument parser and dispatch logic get full coverage by mocking the send_sms functions main.py calls, so no real network or file I/O occurs; streamlit_app.py's pure, non-UI helper functions (no internal st.* calls) get direct coverage. It deliberately does not attempt any test of streamlit_app.py's Streamlit-dependent rendering/interaction code (tabs, forms, session state, widgets, main()) — that would require a dedicated harness such as streamlit.testing.v1.AppTest and is a materially larger undertaking than 'add tests'; it is left as an explicitly documented residual limitation rather than improvised now (P13). It makes exactly two small, behavior-preserving changes to production code, both purely to enable testing: main() gains an optional argv parameter (default None preserves today's sys.argv-reading behavior exactly), and streamlit_app.py's module-level st.set_page_config() call moves inside its existing `if __name__ == "__main__":` guard (so `streamlit run streamlit_app.py`'s actual behavior and command ordering are unchanged, but a bare `import streamlit_app` no longer requires a live Streamlit script context). No new third-party test dependency is introduced — everything uses Python's standard library unittest.mock.

---

# Current State

project/main.py's main() calls `parser.parse_args()` with no arguments (reading real sys.argv) and has no argv parameter today. build_parser() defines six subcommands: send (--phone, --message, --timeout), send-batch (--gate, --batch-size, --pause-seconds, --dry-run, --continue-on-error, --timeout), supplement (same shape as send-batch), find-one (--gate, --number, --dry-run, --timeout), find-sheet (--gate, --pause-seconds, --dry-run, --continue-on-error, --timeout), and duplicates (--gate only, no --timeout). main() imports and calls exactly one of six send_sms functions per subcommand (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore, najit_duplikaty) inside a try/except catching (ConfigurationError, SpreadsheetError, ValueError) and returning exit code 2; each command branch prints JSON and returns 0 or 1 depending on the result(s)' `ok` field, except duplicates which always returns 0. No test file for main.py exists; project/tests/test_send_sms.py is the only test file (13 tests). project/streamlit_app.py has zero tests. Its module executes `st.set_page_config(page_title="Sprava GSM zavor", layout="wide")` at module level (lines 33-36), immediately after its imports and before any function is defined — this is the only Streamlit command executed at import time; every other `st.*` call lives inside a function body. The file ends with `if __name__ == "__main__": main()` (lines 816-817). Its pure helper functions — gate_label(gate: GateConfig) -> str, rows_dataframe(analysis: SheetAnalysis, *, statuses=None) -> pd.DataFrame, editable_numbers_dataframe(analysis: SheetAnalysis) -> pd.DataFrame, messages_dataframe(messages: Sequence[str]) -> pd.DataFrame, and results_dataframe(results: Sequence[SmsResult]) -> pd.DataFrame — contain no `st.*` calls internally. project/README.md's 'Current limitations' section currently contains the bullet 'No automated tests exist for `main.py` (CLI argument parsing / exit codes) or for `streamlit_app.py`.'

---

# Inputs

The existing project/main.py (build_parser, main, and its six send_sms imports) and project/streamlit_app.py (its module-level st.set_page_config call, its `if __name__ == "__main__":` guard, and its five named pure helper functions); Python's standard library unittest and unittest.mock; the existing test conventions in project/tests/test_send_sms.py; project/README.md's current 'Current capabilities (v0.1)' and 'Current limitations' sections.

---

# Outputs

Modified project/main.py: main() gains an optional argv parameter. New project/tests/test_main.py: unit tests for build_parser() and main()'s dispatch logic. Modified project/streamlit_app.py: the module-level st.set_page_config() call relocated inside the `if __name__ == "__main__":` guard; no other line changed. New project/tests/test_streamlit_app.py: unit tests for the five named pure helper functions. Modified project/README.md: the resolved portion of the tests limitation moved into 'Current capabilities (v0.1)', with a new, narrower residual limitation bullet added. No other file is created or modified.

---

# Functional Requirements

## Point 1

SHALL: Add an optional argv parameter to main() in project/main.py: `def main(argv: Sequence[str] | None = None) -> int`, passed as `parser.parse_args(argv)`, so passing None (the default) preserves today's exact behavior of argparse reading real sys.argv.

Acceptance criteria:
- main()'s signature becomes `def main(argv: Sequence[str] | None = None) -> int`
- The call `parser.parse_args()` is changed to `parser.parse_args(argv)`
- The `if __name__ == "__main__": raise SystemExit(main())` block at the bottom of the file is unchanged, so running the script directly still reads real sys.argv exactly as before
- No other line of main.py is changed by this point

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-19T14:47:57+02:00._

Changed main()'s signature from `def main() -> int` to `def main(argv: Sequence[str] | None = None) -> int` and changed `parser.parse_args()` to `parser.parse_args(argv)`. `Sequence` was already imported at the top of main.py. The `if __name__ == "__main__": raise SystemExit(main())` block and every other line of the file are unchanged.

Files touched:
- `project/main.py`

Tests:
- No tests were executed by the programmer, per the contract's explicit Out-of-Scope instruction (permission_profile 'edit' has no Bash access to run python -m unittest/pytest). All 35 new test cases across test_main.py and test_streamlit_app.py were verified by manually tracing each test's logic line-by-line against the real implementations of project/main.py, project/streamlit_app.py, and project/send_sms.py (argument names/types/defaults, dispatch keyword-argument shapes, dataclass field names). Running the full suite (13 existing test_send_sms.py tests plus the new tests) to confirm they all actually pass remains a manual follow-up for the owner, per the established precedent from contracts 0002/0003/0005.

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-19T14:49:48+02:00._

main.py line 121: `def main(argv: Sequence[str] | None = None) -> int`; line 123: `args = parser.parse_args(argv)`. `Sequence` was already imported (line 7). Lines 194-195 `if __name__ == "__main__": raise SystemExit(main())` are byte-for-byte unchanged. Full-file read confirms no other line was touched. Matches the point's acceptance criteria exactly.

## Point 2

SHALL: Add a new project/tests/test_main.py with unit tests for build_parser(), covering all six subcommands' arguments, types, defaults, and required flags, including the --timeout float argument (default send_sms.DEFAULT_SEND_TIMEOUT) present on send/send-batch/supplement/find-one/find-sheet and absent on duplicates.

Acceptance criteria:
- For each of the six subcommands, a test parses a minimal valid argument list (using build_parser().parse_args([...])) and asserts the parsed namespace has the expected attributes and default values (e.g. send-batch's default batch_size=10, pause_seconds=45.0, dry_run=False, continue_on_error=False, timeout=DEFAULT_SEND_TIMEOUT)
- A test confirms --timeout is accepted and correctly overrides the default on each of send, send-batch, supplement, find-one, and find-sheet
- A test confirms the duplicates subcommand's parser does not define a --timeout argument (parsing `duplicates --gate 1 --timeout 5` raises SystemExit/an argparse error)
- A test confirms each subcommand's required arguments (e.g. --phone/--message for send, --gate for the others, --number for find-one) raise SystemExit when omitted, consistent with argparse's required=True behavior

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-19T14:47:57+02:00._

Created project/tests/test_main.py's BuildParserTests class with 18 tests covering all six subcommands: default-value assertions for send, send-batch, supplement, find-one, find-sheet, duplicates (matching the actual defaults read from main.py: batch_size=10, pause_seconds=45.0 for send-batch/supplement, pause_seconds=20.0 for find-sheet, dry_run=False, continue_on_error=False, timeout=DEFAULT_SEND_TIMEOUT); required-argument omission tests (phone/message for send, gate for send-batch/supplement/find-sheet/duplicates, gate+number for find-one) each asserting SystemExit with stderr suppressed via contextlib.redirect_stderr; --timeout override tests for send/send-batch/supplement/find-one/find-sheet; and a test confirming duplicates' parser has no --timeout attribute plus a test confirming passing --timeout to duplicates raises SystemExit (argparse 'unrecognized arguments').

Files touched:
- `project/tests/test_main.py`

Tests:
- No tests were executed by the programmer, per the contract's explicit Out-of-Scope instruction (permission_profile 'edit' has no Bash access to run python -m unittest/pytest). All 35 new test cases across test_main.py and test_streamlit_app.py were verified by manually tracing each test's logic line-by-line against the real implementations of project/main.py, project/streamlit_app.py, and project/send_sms.py (argument names/types/defaults, dispatch keyword-argument shapes, dataclass field names). Running the full suite (13 existing test_send_sms.py tests plus the new tests) to confirm they all actually pass remains a manual follow-up for the owner, per the established precedent from contracts 0002/0003/0005.

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-19T14:49:48+02:00._

test_main.py's BuildParserTests (18 tests) covers all six subcommands. Defaults verified against actual main.py: send-batch/supplement batch_size=10, pause_seconds=45.0; find-sheet pause_seconds=20.0; dry_run=False, continue_on_error=False, timeout=DEFAULT_SEND_TIMEOUT everywhere it applies — all match the real build_parser() code read directly. --timeout override tests present for send/send-batch/supplement/find-one/find-sheet. duplicates' parser correctly has no --timeout attribute (test_duplicates_defaults asserts `not hasattr(args, 'timeout')`) and test_duplicates_rejects_timeout confirms passing --timeout raises SystemExit (argparse unrecognized-argument error), matching the real duplicates_parser which only defines --gate. Required-field omission tests (phone/message, gate, gate+number) all correctly wrapped in redirect_stderr and assertRaises(SystemExit), consistent with argparse's required=True behavior.

## Point 3

SHALL: Add unit tests to project/tests/test_main.py for main()'s dispatch logic, using unittest.mock.patch to replace each of the six send_sms functions imported into the main module's namespace, invoking main() via its new argv parameter with no real network or file I/O.

Acceptance criteria:
- For each of the six subcommands, at least one test patches the corresponding imported function (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore, or najit_duplikaty) in the main module's namespace, calls main(argv=[...]), and asserts the mock was called with arguments matching the parsed CLI flags
- For send, send-batch, supplement, find-one, and find-sheet, at least one test asserts main() returns 0 when the mocked function's result(s) indicate success (ok=True), and at least one test asserts main() returns 1 when they indicate failure (ok=False)
- For duplicates, a test asserts main() returns 0 regardless of the mocked najit_duplikaty's return value (a list), since that branch does not check an ok field
- At least one test asserts that when the mocked function raises ConfigurationError, SpreadsheetError, or ValueError, main() returns 2
- Every test in this point invokes main() through its argv parameter (not by mutating sys.argv) and never calls a real, unmocked send_sms function

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-19T14:47:57+02:00._

Added MainDispatchTests to project/tests/test_main.py with 17 tests. Each of the six send_sms functions imported into main's namespace (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore, najit_duplikaty) is patched via `patch.object(main, "<name>")` and invoked exclusively through `main.main(argv=[...])` via a `_run_main` helper that also suppresses stdout. Assertions verify the mock was called with arguments matching the parsed CLI flags (positional gate/phone/number plus the exact keyword arguments main.py passes, e.g. stop_on_error=not continue_on_error, config_path=Path("config.toml") default). send/send-batch/supplement/find-one/find-sheet each have a success (ok=True -> return 0) and failure (ok=False -> return 1) test. duplicates has two tests (non-empty and empty return value) both asserting return 0, since that branch never checks an ok field. Three tests confirm ConfigurationError, SpreadsheetError, and ValueError each cause main() to return 2. No test mutates sys.argv or calls a real send_sms function.

Files touched:
- `project/tests/test_main.py`

Tests:
- No tests were executed by the programmer, per the contract's explicit Out-of-Scope instruction (permission_profile 'edit' has no Bash access to run python -m unittest/pytest). All 35 new test cases across test_main.py and test_streamlit_app.py were verified by manually tracing each test's logic line-by-line against the real implementations of project/main.py, project/streamlit_app.py, and project/send_sms.py (argument names/types/defaults, dispatch keyword-argument shapes, dataclass field names). Running the full suite (13 existing test_send_sms.py tests plus the new tests) to confirm they all actually pass remains a manual follow-up for the owner, per the established precedent from contracts 0002/0003/0005.

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-19T14:49:48+02:00._

MainDispatchTests (17 tests) patches each of the six imported send_sms functions via patch.object(main, ...) and invokes exclusively through the `_run_main` helper which calls `main.main(argv)` — never mutates sys.argv, never calls an unmocked send_sms function. Cross-checked every mock.assert_called_once_with(...) against main.py's actual call sites (e.g. poslat_davkove_sms's stop_on_error=not args.continue_on_error, config_path=args.config, timeout=args.timeout — all keyword names and positional gate argument match exactly) and against send_sms.py's real function signatures (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore, najit_duplikaty all confirmed keyword-only after the required positional args, matching test call shapes). send/send-batch/supplement/find-one/find-sheet each have an ok=True->0 and ok=False->1 test. duplicates has two tests (non-empty and empty list) both asserting return 0, matching main.py's duplicates branch which never checks 'ok'. Three tests (ConfigurationError, SpreadsheetError, ValueError) each confirm exit code 2, matching main.py's except clause exactly.

## Point 4

SHALL: Relocate project/streamlit_app.py's module-level st.set_page_config(page_title="Sprava GSM zavor", layout="wide") call into the existing `if __name__ == "__main__":` guard, immediately before the call to main(), so the call no longer executes merely by importing the module.

Acceptance criteria:
- The st.set_page_config(...) call no longer appears at module level (outside any function or guard)
- The `if __name__ == "__main__":` block now contains the st.set_page_config(...) call immediately followed by the existing call to main(), in that order
- No other module-level statement in streamlit_app.py executes a Streamlit command outside a function body or this guard (confirmed by reading the full file)
- No function body, argument, or behavior elsewhere in streamlit_app.py is changed by this point

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-19T14:47:57+02:00._

Removed the module-level `st.set_page_config(page_title="Sprava GSM zavor", layout="wide")` call (previously right after the imports, before inject_styles()) and re-added the identical call inside `if __name__ == "__main__":`, immediately before the existing `main()` call. Verified by reading the full file that no other module-level statement (outside a function body or this guard) invokes an `st.*` command — confirmed via a `^st\.` grep returning no matches. No other line, function body, or argument in streamlit_app.py was changed.

Files touched:
- `project/streamlit_app.py`

Tests:
- No tests were executed by the programmer, per the contract's explicit Out-of-Scope instruction (permission_profile 'edit' has no Bash access to run python -m unittest/pytest). All 35 new test cases across test_main.py and test_streamlit_app.py were verified by manually tracing each test's logic line-by-line against the real implementations of project/main.py, project/streamlit_app.py, and project/send_sms.py (argument names/types/defaults, dispatch keyword-argument shapes, dataclass field names). Running the full suite (13 existing test_send_sms.py tests plus the new tests) to confirm they all actually pass remains a manual follow-up for the owner, per the established precedent from contracts 0002/0003/0005.

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-19T14:49:48+02:00._

streamlit_app.py: the module-level st.set_page_config() call no longer appears between imports and inject_styles() (confirmed by reading the full file top to bottom). Lines 810-815 now read `if __name__ == "__main__": st.set_page_config(page_title="Sprava GSM zavor", layout="wide"); main()` — set_page_config immediately followed by main(), in that order. A full-file read confirms every other `st.*` call lives inside a function body (inject_styles, load_config_cached, render_hero, run_messages_ui, render_sheet_health, render_flash_message, render_sheet_editor, main) or this guard — no other bare module-level Streamlit statement exists. No function body, argument, or other behavior was altered.

## Point 5

SHALL: Add a new project/tests/test_streamlit_app.py with unit tests for the pure helper functions gate_label, rows_dataframe, editable_numbers_dataframe, messages_dataframe, and results_dataframe, importing streamlit_app directly.

Acceptance criteria:
- The test file imports streamlit_app directly (e.g. `import streamlit_app` or `from streamlit_app import ...`) and, per the previous point's fix, this import does not execute st.set_page_config() or require a live Streamlit script context
- A test for gate_label asserts it returns the expected '<id>: <sheet>' string for a given GateConfig
- A test for rows_dataframe asserts the returned DataFrame has the expected columns (radek, puvodni_hodnota, normalizovane_cislo, stav, chyba) for a SheetAnalysis with a mix of valid/duplicate/invalid/blank rows, and that passing a `statuses` filter returns only matching rows
- A test for editable_numbers_dataframe asserts the returned DataFrame's 'telefon' column excludes blank rows and includes normalized (or raw, when not normalized) values for the rest
- A test for messages_dataframe asserts the returned DataFrame has 1-based 'poradi' values and a 'prikaz_sms' column matching the input message list
- A test for results_dataframe asserts the returned DataFrame's columns (ok, telefon, zprava, status_code, chyba, odpoved) match a given list of SmsResult objects, including one with a non-None payload serialized into 'odpoved'

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-19T14:47:57+02:00._

Created project/tests/test_streamlit_app.py, importing `streamlit_app` directly (this import no longer requires a live Streamlit script context after Point 4's fix) plus `GateConfig`, `SheetAnalysis`, `SheetRow`, `SmsResult` from send_sms as synthetic fixtures. gate_label is asserted to produce '<id>: <sheet>' from a GateConfig. rows_dataframe is tested against a hand-built SheetAnalysis containing one valid, one duplicate, one invalid, and one blank row: asserts the exact column list (radek, puvodni_hodnota, normalizovane_cislo, stav, chyba), row count, and that a `statuses=("valid","duplicate")` filter returns only those two rows. editable_numbers_dataframe is asserted to produce a single 'telefon' column excluding the blank row, using normalized values where present and the raw value for the invalid row. messages_dataframe is asserted to produce 1-based 'poradi' values and a 'prikaz_sms' column matching the input list exactly. results_dataframe is asserted against the exact column list (ok, telefon, zprava, status_code, chyba, odpoved) using two SmsResult objects — one with a non-None payload (asserting 'odpoved' equals json.dumps of that payload) and one with error set and no payload (asserting 'odpoved' == "" and 'chyba' matches the error).

Files touched:
- `project/tests/test_streamlit_app.py`

Tests:
- No tests were executed by the programmer, per the contract's explicit Out-of-Scope instruction (permission_profile 'edit' has no Bash access to run python -m unittest/pytest). All 35 new test cases across test_main.py and test_streamlit_app.py were verified by manually tracing each test's logic line-by-line against the real implementations of project/main.py, project/streamlit_app.py, and project/send_sms.py (argument names/types/defaults, dispatch keyword-argument shapes, dataclass field names). Running the full suite (13 existing test_send_sms.py tests plus the new tests) to confirm they all actually pass remains a manual follow-up for the owner, per the established precedent from contracts 0002/0003/0005.

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-19T14:49:48+02:00._

test_streamlit_app.py imports `streamlit_app` directly (safe post-Point-4) plus GateConfig/SheetAnalysis/SheetRow/SmsResult from send_sms, whose field names (id/phone/password/sheet; row_number/raw_value/normalized/status/error; ok/phone/message/status_code/payload/error) were verified against the actual dataclass definitions in send_sms.py and match exactly. gate_label test asserts '3: 3 - Namesti' matching the real f'{gate.id}: {gate.sheet}' implementation. rows_dataframe test asserts the exact column list (radek, puvodni_hodnota, normalizovane_cislo, stav, chyba) against a 4-row fixture (valid/duplicate/invalid/blank) and a statuses filter test correctly returns only 2 rows. editable_numbers_dataframe test asserts a single 'telefon' column of 3 values (blank excluded), using normalized where present and raw for the invalid row, matching `row.normalized or row.raw_value for row in analysis.rows if row.status != 'blank'`. messages_dataframe test asserts 1-based poradi and matching prikaz_sms values. results_dataframe test asserts the exact column list (ok, telefon, zprava, status_code, chyba, odpoved), a payload correctly serialized via json.dumps into 'odpoved', and an errored/no-payload result yielding odpoved=''.

## Point 6

SHALL: Update project/README.md: move the resolved portion of the 'No automated tests exist for main.py ... or for streamlit_app.py' limitation into 'Current capabilities (v0.1)' describing exactly what is now covered, and add a narrower residual limitation bullet stating that streamlit_app.py's Streamlit-dependent rendering/interaction code remains untested.

Acceptance criteria:
- The 'Current limitations' section no longer contains the original 'No automated tests exist for main.py ... or for streamlit_app.py' bullet
- The 'Current capabilities (v0.1)' section contains a new bullet or clause stating that main.py's argument parsing and dispatch logic, and streamlit_app.py's pure data-transformation helper functions, are now covered by automated tests
- The 'Current limitations' section contains a new, narrower bullet stating that streamlit_app.py's Streamlit-dependent rendering/interaction code (tabs, forms, session state, widgets, main()) remains untested, and that covering it is deferred to a possible future contract
- The other existing 'Current limitations' bullet (stale-lock recovery) remains present and unaltered, and no other section of project/README.md is modified

> Status: APPROVED

Programmer note:

_By `programmer`, 2026-08-19T14:47:57+02:00._

Removed the 'No automated tests exist for main.py ... or for streamlit_app.py' bullet from 'Current limitations'. Added two new bullets to 'Current capabilities (v0.1)' listing tests/test_main.py (argument parsing + mocked dispatch coverage) and tests/test_streamlit_app.py (pure helper function coverage). Added a new, narrower 'Current limitations' bullet naming streamlit_app.py's Streamlit-dependent rendering/interaction code (tabs, forms, session state, widgets, main()) as still untested and deferred to a possible future contract. The pre-existing stale-lock-recovery limitation bullet, the 'Current capabilities' test_send_sms.py bullet (including its pre-existing '8 tests' text, which is outside this contract's scope), and every other section of the README are unchanged.

Files touched:
- `project/README.md`

Tests:
- No tests were executed by the programmer, per the contract's explicit Out-of-Scope instruction (permission_profile 'edit' has no Bash access to run python -m unittest/pytest). All 35 new test cases across test_main.py and test_streamlit_app.py were verified by manually tracing each test's logic line-by-line against the real implementations of project/main.py, project/streamlit_app.py, and project/send_sms.py (argument names/types/defaults, dispatch keyword-argument shapes, dataclass field names). Running the full suite (13 existing test_send_sms.py tests plus the new tests) to confirm they all actually pass remains a manual follow-up for the owner, per the established precedent from contracts 0002/0003/0005.

Reviewer's implementation review for this point:

_By `reviewer`, 2026-08-19T14:49:48+02:00._

README.md's 'Current limitations' no longer contains the original 'No automated tests exist for main.py ... or for streamlit_app.py' bullet. 'Current capabilities (v0.1)' gained two new bullets describing exactly what test_main.py and test_streamlit_app.py cover, matching the actual test content verified above. 'Current limitations' gained a new, narrower bullet naming streamlit_app.py's Streamlit-dependent rendering/interaction code (tabs, forms, session-state handling, widgets, main()) as untested and deferred. The pre-existing stale-lock-recovery limitation bullet is present and unaltered. No other README section (Purpose, Development environment, Planned evolution) was modified. The pre-existing '8 tests' text on the test_send_sms.py bullet was correctly left untouched, consistent with this being outside this contract's scope (already noted as such in the accepted Architecture Review).

---

# Out of Scope

This contract SHALL NOT add any test of streamlit_app.py's Streamlit-dependent rendering/interaction code (inject_styles, load_config_cached, load_analysis_cached, render_hero, render_result_summary, run_messages_ui, render_sheet_health, render_flash_message, render_sheet_editor, main()) — that requires a dedicated harness (e.g. streamlit.testing.v1.AppTest) and is deferred, not attempted here. It SHALL NOT add any new third-party dependency; only Python's standard library (unittest, unittest.mock) is used. It SHALL NOT change main()'s or any subcommand's existing behavior, arguments, or defaults beyond adding the argv parameter — that parameter's default (None) must reproduce today's exact sys.argv-reading behavior. It SHALL NOT change streamlit_app.py's actual runtime behavior when executed via `streamlit run streamlit_app.py` — only the internal placement of one call, not its effect or timing relative to script execution, changes. It SHALL NOT modify project/send_sms.py. It SHALL NOT execute the test suite as part of the programmer's own verification — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash access to run `python -m unittest`/pytest; the programmer instead verifies each new test's correctness by reading and tracing its logic against the implementation, and actually running the full suite (expected 13 existing tests plus the new test_main.py and test_streamlit_app.py tests) to confirm they all pass is a manual follow-up for the owner after this contract is committed, per the established precedent from IMPLEMENTATION_CONTRACT_0002/0003/0005. It SHALL NOT modify any section of project/README.md other than the one named bullet's move and rewording.

---

# Acceptance Criteria

Acceptance criteria are listed per point in the Functional Requirements section.

---

# Architecture Review

### Round 1 — 2026-08-19T14:43:41+02:00 — Verdict: ACCEPTED — Reviewer: `reviewer`

Verified against AGENTS.md, PRINCIPLES.md, memory/DECISIONS.md (ADR-021/022 write-scope rules, ADR-008 naming convention, decision 7 risk_level criteria), and the actual current source (project/main.py, project/streamlit_app.py, project/send_sms.py, project/tests/test_send_sms.py, project/README.md).

1) Purpose/Intent: matches a real, already-documented backlog item (project/README.md's 'Current limitations' bullet 'No automated tests exist for main.py ... or for streamlit_app.py'), not a speculative future need — consistent with P1/P15. It deliberately excludes Streamlit-UI-dependent code as a documented residual limitation rather than improvising a bigger harness now, correctly citing P13.

2) Factual accuracy of Current State — checked line by line against the real files, all confirmed exact: main.py's build_parser() six subcommands and their flags (including --timeout present on send/send-batch/supplement/find-one/find-sheet, absent on duplicates) match exactly; main()'s current `parser.parse_args()` call and the unchanged `if __name__ == "__main__": raise SystemExit(main())` block match exactly (lines 121-195); the try/except catching (ConfigurationError, SpreadsheetError, ValueError) returning 2, and the duplicates branch always returning 0, match exactly. streamlit_app.py's st.set_page_config() at lines 33-36 (module level, before any function def) and the `if __name__ == "__main__": main()` guard at lines 816-817 match exactly; the five named helper functions (gate_label, rows_dataframe, editable_numbers_dataframe, messages_dataframe, results_dataframe) contain no internal st.* calls, confirmed by reading the full file. SmsResult/SheetRow/GateConfig field names referenced in Point 5's acceptance criteria (ok, phone, message, status_code, payload, error; row_number, raw_value, normalized, status, error) all match send_sms.py's actual dataclasses. test_send_sms.py actually has 13 tests (grep count confirmed), matching the contract's claim, even though README.md's stale 'Current capabilities' text separately says '8 tests' — that pre-existing README inconsistency is outside this contract's stated scope (Point 6 only touches the one named limitations bullet) and does not make the contract's own Current State inaccurate.

3) Points are actionable and correctly ordered: Point 1 (main.py argv param) precedes Point 3 (dispatch tests using that argv param); Point 4 (streamlit_app.py set_page_config relocation) precedes Point 5 (tests that rely on bare import not requiring a live Streamlit context). Every point has concrete, checkable acceptance criteria tied to real code shapes already verified above (e.g. send-batch's actual defaults batch_size=10/pause_seconds=45.0 are correct).

4) Out of Scope is explicit and closes the obvious edge cases: no new dependency, no behavior change beyond the argv default and the set_page_config relocation, no touching send_sms.py, no touching other README sections, and explicitly documents why the programmer cannot run the test suite itself (permission_profile 'edit' has no Bash) with a stated precedent (contracts 0002/0003/0005) — consistent with what the programmer's actual profile allows per AGENTS.md/ADR-022.

5) Backward compatibility: both production-code changes are explicitly justified as behavior-preserving (argv=None reproduces sys.argv reading; moving set_page_config keeps it the first Streamlit command executed relative to any other st.* call, since it still runs before main() at script execution time) — no unjustified breakage.

6) Scope/permissions: all touched paths (project/main.py, project/streamlit_app.py, project/tests/test_main.py, project/tests/test_streamlit_app.py, project/README.md) are inside project/, matching ADR-022's default write scope; no framework layer or root governance .md file is touched; nothing destructive is requested.

7) Naming convention: new files test_main.py and test_streamlit_app.py are lowercase_with_underscores, no hyphens, no diacritics, matching the existing test_send_sms.py convention (ADR-008).

8) risk_level check (decision 7): no real credentials/API keys, no real external-system calls (all six send_sms functions are mocked per Point 3's own acceptance criteria), no native/hardware libraries, and no personal/real data risk (only argument-parsing and DataFrame-shape tests with synthetic data). 'standard' is appropriate; no escalation needed.

No defects found. The contract is ready for the programmer as written.

---

# Future Evolution

Full Streamlit UI/interaction test coverage for streamlit_app.py (tabs, forms, session state, live widget behavior, main() itself), likely via streamlit.testing.v1.AppTest or an equivalent harness, is deferred to a future contract if it turns out to be worth the additional tooling investment — not designed now (P1/P15). The other residual limitation already documented in project/README.md (stale-lock recovery) remains deferred to its own future contract, untouched by this change.

---

# Completion Notes

Implemented all 6 points of IMPLEMENTATION_CONTRACT_0006. Added an optional argv parameter to main.py's main() (default None preserves current sys.argv-reading behavior); added project/tests/test_main.py with full build_parser() coverage (defaults, required-argument SystemExit checks, --timeout override/absence across all six subcommands) and main() dispatch coverage (all six send_sms functions mocked via unittest.mock.patch.object, success/failure exit codes, duplicates' always-0 behavior, and exception-to-exit-code-2 mapping for ConfigurationError/SpreadsheetError/ValueError); relocated streamlit_app.py's module-level st.set_page_config() call into the existing `if __name__ == "__main__":` guard immediately before main(); added project/tests/test_streamlit_app.py covering the five named pure helper functions (gate_label, rows_dataframe, editable_numbers_dataframe, messages_dataframe, results_dataframe) by importing streamlit_app directly and constructing send_sms dataclasses (GateConfig, SheetAnalysis, SheetRow, SmsResult) as synthetic fixtures; updated project/README.md moving the resolved test-coverage limitation into 'Current capabilities (v0.1)' as two new bullets and replacing it in 'Current limitations' with a narrower bullet naming the still-untested Streamlit-dependent rendering/interaction code, deferred to a possible future contract. Per the contract's explicit Out-of-Scope instruction, the test suite was not executed by the programmer (permission_profile 'edit' has no Bash access); all new tests were verified by reading and tracing their logic against the actual implementation of main.py, streamlit_app.py, and send_sms.py line by line, matching argument names, defaults, dataclass field names, and control-flow branches exactly as they exist in the current source. No architectural gaps or ambiguities were encountered — every point had unambiguous, concrete acceptance criteria traceable to real code shapes.

---

# Implementation Review

### Round 1 — 2026-08-19T14:49:48+02:00 — Verdict: APPROVED — Reviewer: `reviewer`

All 6 points of IMPLEMENTATION_CONTRACT_0006 are correctly implemented and verified against actual source. main.py's main() gains an optional argv parameter (default None, parser.parse_args(argv)) with zero other line changes; project/tests/test_main.py provides full build_parser() coverage (defaults, required-field SystemExit, --timeout override/absence) for all six subcommands and full dispatch coverage (all six send_sms functions patched via patch.object, argv-only invocation, success/failure exit codes, duplicates' always-0 behavior, exception-to-exit-2 mapping) — every mock call assertion was checked line-by-line against main.py's actual positional/keyword call shapes and against send_sms.py's actual function signatures, and all match exactly. streamlit_app.py's module-level st.set_page_config() call was correctly relocated inside `if __name__ == "__main__":`, immediately before main(), with no other line touched (confirmed no other module-level `st.*` call exists). project/tests/test_streamlit_app.py directly imports streamlit_app (now import-safe post-Point-4) and covers all five named pure helpers with fixtures built from send_sms's real dataclasses (GateConfig, SheetAnalysis, SheetRow, SmsResult), whose field names were verified against the actual dataclass definitions. project/README.md correctly moves the resolved limitation bullet into 'Current capabilities' as two new bullets and replaces it with a narrower, correctly-scoped residual limitation bullet; the stale-lock bullet and all other README sections are unchanged.

Out of Scope check: OK — Discovery diff lists: added project/tests/test_main.py and project/tests/test_streamlit_app.py (exactly the two new test files the contract's Outputs section calls for); changed project/README.md, project/main.py, project/streamlit_app.py (exactly the three modified files the contract's Outputs section calls for, and content-checked above to confirm each change is in-scope and no unrelated line was touched); changed agents/architect/WORKING_STATE.md and agents/programmer/runtime/session.log, both confirmed to be auto-generated framework bookkeeping files (WORKING_STATE.md's own header states 'Generated automatically from the live contract queue on every state change ... do not edit by hand') produced as a side effect of the contract pipeline transitioning this contract's status, not manual programmer edits and not governed by this contract's Outputs section. No send_sms.py change, no new third-party dependency, no test-suite execution by the programmer, and no other file creation beyond the contract's stated Outputs.

---

# Lessons Learned

_Not filled in._

---

<!-- CONTRACT-META
{
  "number": 6,
  "title": "Add automated test coverage for main.py and streamlit_app.py's pure helpers",
  "status": "APPROVED",
  "created_by": "architect",
  "assigned_to": "owner",
  "handoff_to": "owner",
  "created_at": "2026-08-19T14:41:41+02:00",
  "updated_at": "2026-08-19T14:49:48+02:00",
  "points": [
    {
      "number": 1,
      "assignment": "Add an optional argv parameter to main() in project/main.py: `def main(argv: Sequence[str] | None = None) -> int`, passed as `parser.parse_args(argv)`, so passing None (the default) preserves today's exact behavior of argparse reading real sys.argv.",
      "acceptance_criteria": [
        "main()'s signature becomes `def main(argv: Sequence[str] | None = None) -> int`",
        "The call `parser.parse_args()` is changed to `parser.parse_args(argv)`",
        "The `if __name__ == \"__main__\": raise SystemExit(main())` block at the bottom of the file is unchanged, so running the script directly still reads real sys.argv exactly as before",
        "No other line of main.py is changed by this point"
      ],
      "programmer_note": "Changed main()'s signature from `def main() -> int` to `def main(argv: Sequence[str] | None = None) -> int` and changed `parser.parse_args()` to `parser.parse_args(argv)`. `Sequence` was already imported at the top of main.py. The `if __name__ == \"__main__\": raise SystemExit(main())` block and every other line of the file are unchanged.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-19T14:47:57+02:00",
      "programmer_files": [
        "project/main.py"
      ],
      "programmer_tests": [
        "No tests were executed by the programmer, per the contract's explicit Out-of-Scope instruction (permission_profile 'edit' has no Bash access to run python -m unittest/pytest). All 35 new test cases across test_main.py and test_streamlit_app.py were verified by manually tracing each test's logic line-by-line against the real implementations of project/main.py, project/streamlit_app.py, and project/send_sms.py (argument names/types/defaults, dispatch keyword-argument shapes, dataclass field names). Running the full suite (13 existing test_send_sms.py tests plus the new tests) to confirm they all actually pass remains a manual follow-up for the owner, per the established precedent from contracts 0002/0003/0005."
      ],
      "reviewer_note": "main.py line 121: `def main(argv: Sequence[str] | None = None) -> int`; line 123: `args = parser.parse_args(argv)`. `Sequence` was already imported (line 7). Lines 194-195 `if __name__ == \"__main__\": raise SystemExit(main())` are byte-for-byte unchanged. Full-file read confirms no other line was touched. Matches the point's acceptance criteria exactly.",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-19T14:49:48+02:00",
      "status": "APPROVED"
    },
    {
      "number": 2,
      "assignment": "Add a new project/tests/test_main.py with unit tests for build_parser(), covering all six subcommands' arguments, types, defaults, and required flags, including the --timeout float argument (default send_sms.DEFAULT_SEND_TIMEOUT) present on send/send-batch/supplement/find-one/find-sheet and absent on duplicates.",
      "acceptance_criteria": [
        "For each of the six subcommands, a test parses a minimal valid argument list (using build_parser().parse_args([...])) and asserts the parsed namespace has the expected attributes and default values (e.g. send-batch's default batch_size=10, pause_seconds=45.0, dry_run=False, continue_on_error=False, timeout=DEFAULT_SEND_TIMEOUT)",
        "A test confirms --timeout is accepted and correctly overrides the default on each of send, send-batch, supplement, find-one, and find-sheet",
        "A test confirms the duplicates subcommand's parser does not define a --timeout argument (parsing `duplicates --gate 1 --timeout 5` raises SystemExit/an argparse error)",
        "A test confirms each subcommand's required arguments (e.g. --phone/--message for send, --gate for the others, --number for find-one) raise SystemExit when omitted, consistent with argparse's required=True behavior"
      ],
      "programmer_note": "Created project/tests/test_main.py's BuildParserTests class with 18 tests covering all six subcommands: default-value assertions for send, send-batch, supplement, find-one, find-sheet, duplicates (matching the actual defaults read from main.py: batch_size=10, pause_seconds=45.0 for send-batch/supplement, pause_seconds=20.0 for find-sheet, dry_run=False, continue_on_error=False, timeout=DEFAULT_SEND_TIMEOUT); required-argument omission tests (phone/message for send, gate for send-batch/supplement/find-sheet/duplicates, gate+number for find-one) each asserting SystemExit with stderr suppressed via contextlib.redirect_stderr; --timeout override tests for send/send-batch/supplement/find-one/find-sheet; and a test confirming duplicates' parser has no --timeout attribute plus a test confirming passing --timeout to duplicates raises SystemExit (argparse 'unrecognized arguments').",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-19T14:47:57+02:00",
      "programmer_files": [
        "project/tests/test_main.py"
      ],
      "programmer_tests": [
        "No tests were executed by the programmer, per the contract's explicit Out-of-Scope instruction (permission_profile 'edit' has no Bash access to run python -m unittest/pytest). All 35 new test cases across test_main.py and test_streamlit_app.py were verified by manually tracing each test's logic line-by-line against the real implementations of project/main.py, project/streamlit_app.py, and project/send_sms.py (argument names/types/defaults, dispatch keyword-argument shapes, dataclass field names). Running the full suite (13 existing test_send_sms.py tests plus the new tests) to confirm they all actually pass remains a manual follow-up for the owner, per the established precedent from contracts 0002/0003/0005."
      ],
      "reviewer_note": "test_main.py's BuildParserTests (18 tests) covers all six subcommands. Defaults verified against actual main.py: send-batch/supplement batch_size=10, pause_seconds=45.0; find-sheet pause_seconds=20.0; dry_run=False, continue_on_error=False, timeout=DEFAULT_SEND_TIMEOUT everywhere it applies — all match the real build_parser() code read directly. --timeout override tests present for send/send-batch/supplement/find-one/find-sheet. duplicates' parser correctly has no --timeout attribute (test_duplicates_defaults asserts `not hasattr(args, 'timeout')`) and test_duplicates_rejects_timeout confirms passing --timeout raises SystemExit (argparse unrecognized-argument error), matching the real duplicates_parser which only defines --gate. Required-field omission tests (phone/message, gate, gate+number) all correctly wrapped in redirect_stderr and assertRaises(SystemExit), consistent with argparse's required=True behavior.",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-19T14:49:48+02:00",
      "status": "APPROVED"
    },
    {
      "number": 3,
      "assignment": "Add unit tests to project/tests/test_main.py for main()'s dispatch logic, using unittest.mock.patch to replace each of the six send_sms functions imported into the main module's namespace, invoking main() via its new argv parameter with no real network or file I/O.",
      "acceptance_criteria": [
        "For each of the six subcommands, at least one test patches the corresponding imported function (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore, or najit_duplikaty) in the main module's namespace, calls main(argv=[...]), and asserts the mock was called with arguments matching the parsed CLI flags",
        "For send, send-batch, supplement, find-one, and find-sheet, at least one test asserts main() returns 0 when the mocked function's result(s) indicate success (ok=True), and at least one test asserts main() returns 1 when they indicate failure (ok=False)",
        "For duplicates, a test asserts main() returns 0 regardless of the mocked najit_duplikaty's return value (a list), since that branch does not check an ok field",
        "At least one test asserts that when the mocked function raises ConfigurationError, SpreadsheetError, or ValueError, main() returns 2",
        "Every test in this point invokes main() through its argv parameter (not by mutating sys.argv) and never calls a real, unmocked send_sms function"
      ],
      "programmer_note": "Added MainDispatchTests to project/tests/test_main.py with 17 tests. Each of the six send_sms functions imported into main's namespace (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore, najit_duplikaty) is patched via `patch.object(main, \"<name>\")` and invoked exclusively through `main.main(argv=[...])` via a `_run_main` helper that also suppresses stdout. Assertions verify the mock was called with arguments matching the parsed CLI flags (positional gate/phone/number plus the exact keyword arguments main.py passes, e.g. stop_on_error=not continue_on_error, config_path=Path(\"config.toml\") default). send/send-batch/supplement/find-one/find-sheet each have a success (ok=True -> return 0) and failure (ok=False -> return 1) test. duplicates has two tests (non-empty and empty return value) both asserting return 0, since that branch never checks an ok field. Three tests confirm ConfigurationError, SpreadsheetError, and ValueError each cause main() to return 2. No test mutates sys.argv or calls a real send_sms function.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-19T14:47:57+02:00",
      "programmer_files": [
        "project/tests/test_main.py"
      ],
      "programmer_tests": [
        "No tests were executed by the programmer, per the contract's explicit Out-of-Scope instruction (permission_profile 'edit' has no Bash access to run python -m unittest/pytest). All 35 new test cases across test_main.py and test_streamlit_app.py were verified by manually tracing each test's logic line-by-line against the real implementations of project/main.py, project/streamlit_app.py, and project/send_sms.py (argument names/types/defaults, dispatch keyword-argument shapes, dataclass field names). Running the full suite (13 existing test_send_sms.py tests plus the new tests) to confirm they all actually pass remains a manual follow-up for the owner, per the established precedent from contracts 0002/0003/0005."
      ],
      "reviewer_note": "MainDispatchTests (17 tests) patches each of the six imported send_sms functions via patch.object(main, ...) and invokes exclusively through the `_run_main` helper which calls `main.main(argv)` — never mutates sys.argv, never calls an unmocked send_sms function. Cross-checked every mock.assert_called_once_with(...) against main.py's actual call sites (e.g. poslat_davkove_sms's stop_on_error=not args.continue_on_error, config_path=args.config, timeout=args.timeout — all keyword names and positional gate argument match exactly) and against send_sms.py's real function signatures (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore, najit_duplikaty all confirmed keyword-only after the required positional args, matching test call shapes). send/send-batch/supplement/find-one/find-sheet each have an ok=True->0 and ok=False->1 test. duplicates has two tests (non-empty and empty list) both asserting return 0, matching main.py's duplicates branch which never checks 'ok'. Three tests (ConfigurationError, SpreadsheetError, ValueError) each confirm exit code 2, matching main.py's except clause exactly.",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-19T14:49:48+02:00",
      "status": "APPROVED"
    },
    {
      "number": 4,
      "assignment": "Relocate project/streamlit_app.py's module-level st.set_page_config(page_title=\"Sprava GSM zavor\", layout=\"wide\") call into the existing `if __name__ == \"__main__\":` guard, immediately before the call to main(), so the call no longer executes merely by importing the module.",
      "acceptance_criteria": [
        "The st.set_page_config(...) call no longer appears at module level (outside any function or guard)",
        "The `if __name__ == \"__main__\":` block now contains the st.set_page_config(...) call immediately followed by the existing call to main(), in that order",
        "No other module-level statement in streamlit_app.py executes a Streamlit command outside a function body or this guard (confirmed by reading the full file)",
        "No function body, argument, or behavior elsewhere in streamlit_app.py is changed by this point"
      ],
      "programmer_note": "Removed the module-level `st.set_page_config(page_title=\"Sprava GSM zavor\", layout=\"wide\")` call (previously right after the imports, before inject_styles()) and re-added the identical call inside `if __name__ == \"__main__\":`, immediately before the existing `main()` call. Verified by reading the full file that no other module-level statement (outside a function body or this guard) invokes an `st.*` command — confirmed via a `^st\\.` grep returning no matches. No other line, function body, or argument in streamlit_app.py was changed.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-19T14:47:57+02:00",
      "programmer_files": [
        "project/streamlit_app.py"
      ],
      "programmer_tests": [
        "No tests were executed by the programmer, per the contract's explicit Out-of-Scope instruction (permission_profile 'edit' has no Bash access to run python -m unittest/pytest). All 35 new test cases across test_main.py and test_streamlit_app.py were verified by manually tracing each test's logic line-by-line against the real implementations of project/main.py, project/streamlit_app.py, and project/send_sms.py (argument names/types/defaults, dispatch keyword-argument shapes, dataclass field names). Running the full suite (13 existing test_send_sms.py tests plus the new tests) to confirm they all actually pass remains a manual follow-up for the owner, per the established precedent from contracts 0002/0003/0005."
      ],
      "reviewer_note": "streamlit_app.py: the module-level st.set_page_config() call no longer appears between imports and inject_styles() (confirmed by reading the full file top to bottom). Lines 810-815 now read `if __name__ == \"__main__\": st.set_page_config(page_title=\"Sprava GSM zavor\", layout=\"wide\"); main()` — set_page_config immediately followed by main(), in that order. A full-file read confirms every other `st.*` call lives inside a function body (inject_styles, load_config_cached, render_hero, run_messages_ui, render_sheet_health, render_flash_message, render_sheet_editor, main) or this guard — no other bare module-level Streamlit statement exists. No function body, argument, or other behavior was altered.",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-19T14:49:48+02:00",
      "status": "APPROVED"
    },
    {
      "number": 5,
      "assignment": "Add a new project/tests/test_streamlit_app.py with unit tests for the pure helper functions gate_label, rows_dataframe, editable_numbers_dataframe, messages_dataframe, and results_dataframe, importing streamlit_app directly.",
      "acceptance_criteria": [
        "The test file imports streamlit_app directly (e.g. `import streamlit_app` or `from streamlit_app import ...`) and, per the previous point's fix, this import does not execute st.set_page_config() or require a live Streamlit script context",
        "A test for gate_label asserts it returns the expected '<id>: <sheet>' string for a given GateConfig",
        "A test for rows_dataframe asserts the returned DataFrame has the expected columns (radek, puvodni_hodnota, normalizovane_cislo, stav, chyba) for a SheetAnalysis with a mix of valid/duplicate/invalid/blank rows, and that passing a `statuses` filter returns only matching rows",
        "A test for editable_numbers_dataframe asserts the returned DataFrame's 'telefon' column excludes blank rows and includes normalized (or raw, when not normalized) values for the rest",
        "A test for messages_dataframe asserts the returned DataFrame has 1-based 'poradi' values and a 'prikaz_sms' column matching the input message list",
        "A test for results_dataframe asserts the returned DataFrame's columns (ok, telefon, zprava, status_code, chyba, odpoved) match a given list of SmsResult objects, including one with a non-None payload serialized into 'odpoved'"
      ],
      "programmer_note": "Created project/tests/test_streamlit_app.py, importing `streamlit_app` directly (this import no longer requires a live Streamlit script context after Point 4's fix) plus `GateConfig`, `SheetAnalysis`, `SheetRow`, `SmsResult` from send_sms as synthetic fixtures. gate_label is asserted to produce '<id>: <sheet>' from a GateConfig. rows_dataframe is tested against a hand-built SheetAnalysis containing one valid, one duplicate, one invalid, and one blank row: asserts the exact column list (radek, puvodni_hodnota, normalizovane_cislo, stav, chyba), row count, and that a `statuses=(\"valid\",\"duplicate\")` filter returns only those two rows. editable_numbers_dataframe is asserted to produce a single 'telefon' column excluding the blank row, using normalized values where present and the raw value for the invalid row. messages_dataframe is asserted to produce 1-based 'poradi' values and a 'prikaz_sms' column matching the input list exactly. results_dataframe is asserted against the exact column list (ok, telefon, zprava, status_code, chyba, odpoved) using two SmsResult objects — one with a non-None payload (asserting 'odpoved' equals json.dumps of that payload) and one with error set and no payload (asserting 'odpoved' == \"\" and 'chyba' matches the error).",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-19T14:47:57+02:00",
      "programmer_files": [
        "project/tests/test_streamlit_app.py"
      ],
      "programmer_tests": [
        "No tests were executed by the programmer, per the contract's explicit Out-of-Scope instruction (permission_profile 'edit' has no Bash access to run python -m unittest/pytest). All 35 new test cases across test_main.py and test_streamlit_app.py were verified by manually tracing each test's logic line-by-line against the real implementations of project/main.py, project/streamlit_app.py, and project/send_sms.py (argument names/types/defaults, dispatch keyword-argument shapes, dataclass field names). Running the full suite (13 existing test_send_sms.py tests plus the new tests) to confirm they all actually pass remains a manual follow-up for the owner, per the established precedent from contracts 0002/0003/0005."
      ],
      "reviewer_note": "test_streamlit_app.py imports `streamlit_app` directly (safe post-Point-4) plus GateConfig/SheetAnalysis/SheetRow/SmsResult from send_sms, whose field names (id/phone/password/sheet; row_number/raw_value/normalized/status/error; ok/phone/message/status_code/payload/error) were verified against the actual dataclass definitions in send_sms.py and match exactly. gate_label test asserts '3: 3 - Namesti' matching the real f'{gate.id}: {gate.sheet}' implementation. rows_dataframe test asserts the exact column list (radek, puvodni_hodnota, normalizovane_cislo, stav, chyba) against a 4-row fixture (valid/duplicate/invalid/blank) and a statuses filter test correctly returns only 2 rows. editable_numbers_dataframe test asserts a single 'telefon' column of 3 values (blank excluded), using normalized where present and raw for the invalid row, matching `row.normalized or row.raw_value for row in analysis.rows if row.status != 'blank'`. messages_dataframe test asserts 1-based poradi and matching prikaz_sms values. results_dataframe test asserts the exact column list (ok, telefon, zprava, status_code, chyba, odpoved), a payload correctly serialized via json.dumps into 'odpoved', and an errored/no-payload result yielding odpoved=''.",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-19T14:49:48+02:00",
      "status": "APPROVED"
    },
    {
      "number": 6,
      "assignment": "Update project/README.md: move the resolved portion of the 'No automated tests exist for main.py ... or for streamlit_app.py' limitation into 'Current capabilities (v0.1)' describing exactly what is now covered, and add a narrower residual limitation bullet stating that streamlit_app.py's Streamlit-dependent rendering/interaction code remains untested.",
      "acceptance_criteria": [
        "The 'Current limitations' section no longer contains the original 'No automated tests exist for main.py ... or for streamlit_app.py' bullet",
        "The 'Current capabilities (v0.1)' section contains a new bullet or clause stating that main.py's argument parsing and dispatch logic, and streamlit_app.py's pure data-transformation helper functions, are now covered by automated tests",
        "The 'Current limitations' section contains a new, narrower bullet stating that streamlit_app.py's Streamlit-dependent rendering/interaction code (tabs, forms, session state, widgets, main()) remains untested, and that covering it is deferred to a possible future contract",
        "The other existing 'Current limitations' bullet (stale-lock recovery) remains present and unaltered, and no other section of project/README.md is modified"
      ],
      "programmer_note": "Removed the 'No automated tests exist for main.py ... or for streamlit_app.py' bullet from 'Current limitations'. Added two new bullets to 'Current capabilities (v0.1)' listing tests/test_main.py (argument parsing + mocked dispatch coverage) and tests/test_streamlit_app.py (pure helper function coverage). Added a new, narrower 'Current limitations' bullet naming streamlit_app.py's Streamlit-dependent rendering/interaction code (tabs, forms, session state, widgets, main()) as still untested and deferred to a possible future contract. The pre-existing stale-lock-recovery limitation bullet, the 'Current capabilities' test_send_sms.py bullet (including its pre-existing '8 tests' text, which is outside this contract's scope), and every other section of the README are unchanged.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-19T14:47:57+02:00",
      "programmer_files": [
        "project/README.md"
      ],
      "programmer_tests": [
        "No tests were executed by the programmer, per the contract's explicit Out-of-Scope instruction (permission_profile 'edit' has no Bash access to run python -m unittest/pytest). All 35 new test cases across test_main.py and test_streamlit_app.py were verified by manually tracing each test's logic line-by-line against the real implementations of project/main.py, project/streamlit_app.py, and project/send_sms.py (argument names/types/defaults, dispatch keyword-argument shapes, dataclass field names). Running the full suite (13 existing test_send_sms.py tests plus the new tests) to confirm they all actually pass remains a manual follow-up for the owner, per the established precedent from contracts 0002/0003/0005."
      ],
      "reviewer_note": "README.md's 'Current limitations' no longer contains the original 'No automated tests exist for main.py ... or for streamlit_app.py' bullet. 'Current capabilities (v0.1)' gained two new bullets describing exactly what test_main.py and test_streamlit_app.py cover, matching the actual test content verified above. 'Current limitations' gained a new, narrower bullet naming streamlit_app.py's Streamlit-dependent rendering/interaction code (tabs, forms, session-state handling, widgets, main()) as untested and deferred. The pre-existing stale-lock-recovery limitation bullet is present and unaltered. No other README section (Purpose, Development environment, Planned evolution) was modified. The pre-existing '8 tests' text on the test_send_sms.py bullet was correctly left untouched, consistent with this being outside this contract's scope (already noted as such in the accepted Architecture Review).",
      "reviewer_note_author": "reviewer",
      "reviewer_note_at": "2026-08-19T14:49:48+02:00",
      "status": "APPROVED"
    }
  ],
  "implementer": "programmer",
  "reviewer": "reviewer",
  "risk_level": "standard",
  "purpose": "project/main.py (the CLI) and project/streamlit_app.py (the web UI) are the two user-facing surfaces of the SMS gateway tool and currently have zero automated test coverage, unlike project/send_sms.py's core logic (13 tests). A regression in CLI argument parsing, dispatch, or exit-code logic, or in the Streamlit app's data-transformation helpers, would only be caught by manual testing today. This closes the last remaining item from the architect's original code review queue by adding real, targeted coverage wherever it is safely and deterministically achievable without a live network, a live Excel file, or a running Streamlit server.",
  "intent": "This adds test coverage where it is safely and deterministically achievable: main.py's argument parser and dispatch logic get full coverage by mocking the send_sms functions main.py calls, so no real network or file I/O occurs; streamlit_app.py's pure, non-UI helper functions (no internal st.* calls) get direct coverage. It deliberately does not attempt any test of streamlit_app.py's Streamlit-dependent rendering/interaction code (tabs, forms, session state, widgets, main()) — that would require a dedicated harness such as streamlit.testing.v1.AppTest and is a materially larger undertaking than 'add tests'; it is left as an explicitly documented residual limitation rather than improvised now (P13). It makes exactly two small, behavior-preserving changes to production code, both purely to enable testing: main() gains an optional argv parameter (default None preserves today's sys.argv-reading behavior exactly), and streamlit_app.py's module-level st.set_page_config() call moves inside its existing `if __name__ == \"__main__\":` guard (so `streamlit run streamlit_app.py`'s actual behavior and command ordering are unchanged, but a bare `import streamlit_app` no longer requires a live Streamlit script context). No new third-party test dependency is introduced — everything uses Python's standard library unittest.mock.",
  "current_state": "project/main.py's main() calls `parser.parse_args()` with no arguments (reading real sys.argv) and has no argv parameter today. build_parser() defines six subcommands: send (--phone, --message, --timeout), send-batch (--gate, --batch-size, --pause-seconds, --dry-run, --continue-on-error, --timeout), supplement (same shape as send-batch), find-one (--gate, --number, --dry-run, --timeout), find-sheet (--gate, --pause-seconds, --dry-run, --continue-on-error, --timeout), and duplicates (--gate only, no --timeout). main() imports and calls exactly one of six send_sms functions per subcommand (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore, najit_duplikaty) inside a try/except catching (ConfigurationError, SpreadsheetError, ValueError) and returning exit code 2; each command branch prints JSON and returns 0 or 1 depending on the result(s)' `ok` field, except duplicates which always returns 0. No test file for main.py exists; project/tests/test_send_sms.py is the only test file (13 tests). project/streamlit_app.py has zero tests. Its module executes `st.set_page_config(page_title=\"Sprava GSM zavor\", layout=\"wide\")` at module level (lines 33-36), immediately after its imports and before any function is defined — this is the only Streamlit command executed at import time; every other `st.*` call lives inside a function body. The file ends with `if __name__ == \"__main__\": main()` (lines 816-817). Its pure helper functions — gate_label(gate: GateConfig) -> str, rows_dataframe(analysis: SheetAnalysis, *, statuses=None) -> pd.DataFrame, editable_numbers_dataframe(analysis: SheetAnalysis) -> pd.DataFrame, messages_dataframe(messages: Sequence[str]) -> pd.DataFrame, and results_dataframe(results: Sequence[SmsResult]) -> pd.DataFrame — contain no `st.*` calls internally. project/README.md's 'Current limitations' section currently contains the bullet 'No automated tests exist for `main.py` (CLI argument parsing / exit codes) or for `streamlit_app.py`.'",
  "inputs": "The existing project/main.py (build_parser, main, and its six send_sms imports) and project/streamlit_app.py (its module-level st.set_page_config call, its `if __name__ == \"__main__\":` guard, and its five named pure helper functions); Python's standard library unittest and unittest.mock; the existing test conventions in project/tests/test_send_sms.py; project/README.md's current 'Current capabilities (v0.1)' and 'Current limitations' sections.",
  "outputs": "Modified project/main.py: main() gains an optional argv parameter. New project/tests/test_main.py: unit tests for build_parser() and main()'s dispatch logic. Modified project/streamlit_app.py: the module-level st.set_page_config() call relocated inside the `if __name__ == \"__main__\":` guard; no other line changed. New project/tests/test_streamlit_app.py: unit tests for the five named pure helper functions. Modified project/README.md: the resolved portion of the tests limitation moved into 'Current capabilities (v0.1)', with a new, narrower residual limitation bullet added. No other file is created or modified.",
  "out_of_scope": "This contract SHALL NOT add any test of streamlit_app.py's Streamlit-dependent rendering/interaction code (inject_styles, load_config_cached, load_analysis_cached, render_hero, render_result_summary, run_messages_ui, render_sheet_health, render_flash_message, render_sheet_editor, main()) — that requires a dedicated harness (e.g. streamlit.testing.v1.AppTest) and is deferred, not attempted here. It SHALL NOT add any new third-party dependency; only Python's standard library (unittest, unittest.mock) is used. It SHALL NOT change main()'s or any subcommand's existing behavior, arguments, or defaults beyond adding the argv parameter — that parameter's default (None) must reproduce today's exact sys.argv-reading behavior. It SHALL NOT change streamlit_app.py's actual runtime behavior when executed via `streamlit run streamlit_app.py` — only the internal placement of one call, not its effect or timing relative to script execution, changes. It SHALL NOT modify project/send_sms.py. It SHALL NOT execute the test suite as part of the programmer's own verification — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash access to run `python -m unittest`/pytest; the programmer instead verifies each new test's correctness by reading and tracing its logic against the implementation, and actually running the full suite (expected 13 existing tests plus the new test_main.py and test_streamlit_app.py tests) to confirm they all pass is a manual follow-up for the owner after this contract is committed, per the established precedent from IMPLEMENTATION_CONTRACT_0002/0003/0005. It SHALL NOT modify any section of project/README.md other than the one named bullet's move and rewording.",
  "future_evolution": "Full Streamlit UI/interaction test coverage for streamlit_app.py (tabs, forms, session state, live widget behavior, main() itself), likely via streamlit.testing.v1.AppTest or an equivalent harness, is deferred to a future contract if it turns out to be worth the additional tooling investment — not designed now (P1/P15). The other residual limitation already documented in project/README.md (stale-lock recovery) remains deferred to its own future contract, untouched by this change.",
  "lessons_learned": "",
  "architecture_review_rounds": [
    {
      "round": 1,
      "date": "2026-08-19T14:43:41+02:00",
      "verdict": "ACCEPTED",
      "reviewer": "reviewer",
      "findings": "Verified against AGENTS.md, PRINCIPLES.md, memory/DECISIONS.md (ADR-021/022 write-scope rules, ADR-008 naming convention, decision 7 risk_level criteria), and the actual current source (project/main.py, project/streamlit_app.py, project/send_sms.py, project/tests/test_send_sms.py, project/README.md).\n\n1) Purpose/Intent: matches a real, already-documented backlog item (project/README.md's 'Current limitations' bullet 'No automated tests exist for main.py ... or for streamlit_app.py'), not a speculative future need — consistent with P1/P15. It deliberately excludes Streamlit-UI-dependent code as a documented residual limitation rather than improvising a bigger harness now, correctly citing P13.\n\n2) Factual accuracy of Current State — checked line by line against the real files, all confirmed exact: main.py's build_parser() six subcommands and their flags (including --timeout present on send/send-batch/supplement/find-one/find-sheet, absent on duplicates) match exactly; main()'s current `parser.parse_args()` call and the unchanged `if __name__ == \"__main__\": raise SystemExit(main())` block match exactly (lines 121-195); the try/except catching (ConfigurationError, SpreadsheetError, ValueError) returning 2, and the duplicates branch always returning 0, match exactly. streamlit_app.py's st.set_page_config() at lines 33-36 (module level, before any function def) and the `if __name__ == \"__main__\": main()` guard at lines 816-817 match exactly; the five named helper functions (gate_label, rows_dataframe, editable_numbers_dataframe, messages_dataframe, results_dataframe) contain no internal st.* calls, confirmed by reading the full file. SmsResult/SheetRow/GateConfig field names referenced in Point 5's acceptance criteria (ok, phone, message, status_code, payload, error; row_number, raw_value, normalized, status, error) all match send_sms.py's actual dataclasses. test_send_sms.py actually has 13 tests (grep count confirmed), matching the contract's claim, even though README.md's stale 'Current capabilities' text separately says '8 tests' — that pre-existing README inconsistency is outside this contract's stated scope (Point 6 only touches the one named limitations bullet) and does not make the contract's own Current State inaccurate.\n\n3) Points are actionable and correctly ordered: Point 1 (main.py argv param) precedes Point 3 (dispatch tests using that argv param); Point 4 (streamlit_app.py set_page_config relocation) precedes Point 5 (tests that rely on bare import not requiring a live Streamlit context). Every point has concrete, checkable acceptance criteria tied to real code shapes already verified above (e.g. send-batch's actual defaults batch_size=10/pause_seconds=45.0 are correct).\n\n4) Out of Scope is explicit and closes the obvious edge cases: no new dependency, no behavior change beyond the argv default and the set_page_config relocation, no touching send_sms.py, no touching other README sections, and explicitly documents why the programmer cannot run the test suite itself (permission_profile 'edit' has no Bash) with a stated precedent (contracts 0002/0003/0005) — consistent with what the programmer's actual profile allows per AGENTS.md/ADR-022.\n\n5) Backward compatibility: both production-code changes are explicitly justified as behavior-preserving (argv=None reproduces sys.argv reading; moving set_page_config keeps it the first Streamlit command executed relative to any other st.* call, since it still runs before main() at script execution time) — no unjustified breakage.\n\n6) Scope/permissions: all touched paths (project/main.py, project/streamlit_app.py, project/tests/test_main.py, project/tests/test_streamlit_app.py, project/README.md) are inside project/, matching ADR-022's default write scope; no framework layer or root governance .md file is touched; nothing destructive is requested.\n\n7) Naming convention: new files test_main.py and test_streamlit_app.py are lowercase_with_underscores, no hyphens, no diacritics, matching the existing test_send_sms.py convention (ADR-008).\n\n8) risk_level check (decision 7): no real credentials/API keys, no real external-system calls (all six send_sms functions are mocked per Point 3's own acceptance criteria), no native/hardware libraries, and no personal/real data risk (only argument-parsing and DataFrame-shape tests with synthetic data). 'standard' is appropriate; no escalation needed.\n\nNo defects found. The contract is ready for the programmer as written."
    }
  ],
  "completion_notes": "Implemented all 6 points of IMPLEMENTATION_CONTRACT_0006. Added an optional argv parameter to main.py's main() (default None preserves current sys.argv-reading behavior); added project/tests/test_main.py with full build_parser() coverage (defaults, required-argument SystemExit checks, --timeout override/absence across all six subcommands) and main() dispatch coverage (all six send_sms functions mocked via unittest.mock.patch.object, success/failure exit codes, duplicates' always-0 behavior, and exception-to-exit-code-2 mapping for ConfigurationError/SpreadsheetError/ValueError); relocated streamlit_app.py's module-level st.set_page_config() call into the existing `if __name__ == \"__main__\":` guard immediately before main(); added project/tests/test_streamlit_app.py covering the five named pure helper functions (gate_label, rows_dataframe, editable_numbers_dataframe, messages_dataframe, results_dataframe) by importing streamlit_app directly and constructing send_sms dataclasses (GateConfig, SheetAnalysis, SheetRow, SmsResult) as synthetic fixtures; updated project/README.md moving the resolved test-coverage limitation into 'Current capabilities (v0.1)' as two new bullets and replacing it in 'Current limitations' with a narrower bullet naming the still-untested Streamlit-dependent rendering/interaction code, deferred to a possible future contract. Per the contract's explicit Out-of-Scope instruction, the test suite was not executed by the programmer (permission_profile 'edit' has no Bash access); all new tests were verified by reading and tracing their logic against the actual implementation of main.py, streamlit_app.py, and send_sms.py line by line, matching argument names, defaults, dataclass field names, and control-flow branches exactly as they exist in the current source. No architectural gaps or ambiguities were encountered — every point had unambiguous, concrete acceptance criteria traceable to real code shapes.",
  "implementation_review_rounds": [
    {
      "round": 1,
      "date": "2026-08-19T14:49:48+02:00",
      "verdict": "APPROVED",
      "reviewer": "reviewer",
      "summary": "All 6 points of IMPLEMENTATION_CONTRACT_0006 are correctly implemented and verified against actual source. main.py's main() gains an optional argv parameter (default None, parser.parse_args(argv)) with zero other line changes; project/tests/test_main.py provides full build_parser() coverage (defaults, required-field SystemExit, --timeout override/absence) for all six subcommands and full dispatch coverage (all six send_sms functions patched via patch.object, argv-only invocation, success/failure exit codes, duplicates' always-0 behavior, exception-to-exit-2 mapping) — every mock call assertion was checked line-by-line against main.py's actual positional/keyword call shapes and against send_sms.py's actual function signatures, and all match exactly. streamlit_app.py's module-level st.set_page_config() call was correctly relocated inside `if __name__ == \"__main__\":`, immediately before main(), with no other line touched (confirmed no other module-level `st.*` call exists). project/tests/test_streamlit_app.py directly imports streamlit_app (now import-safe post-Point-4) and covers all five named pure helpers with fixtures built from send_sms's real dataclasses (GateConfig, SheetAnalysis, SheetRow, SmsResult), whose field names were verified against the actual dataclass definitions. project/README.md correctly moves the resolved limitation bullet into 'Current capabilities' as two new bullets and replaces it with a narrower, correctly-scoped residual limitation bullet; the stale-lock bullet and all other README sections are unchanged.",
      "out_of_scope_ok": true,
      "out_of_scope_findings": "Discovery diff lists: added project/tests/test_main.py and project/tests/test_streamlit_app.py (exactly the two new test files the contract's Outputs section calls for); changed project/README.md, project/main.py, project/streamlit_app.py (exactly the three modified files the contract's Outputs section calls for, and content-checked above to confirm each change is in-scope and no unrelated line was touched); changed agents/architect/WORKING_STATE.md and agents/programmer/runtime/session.log, both confirmed to be auto-generated framework bookkeeping files (WORKING_STATE.md's own header states 'Generated automatically from the live contract queue on every state change ... do not edit by hand') produced as a side effect of the contract pipeline transitioning this contract's status, not manual programmer edits and not governed by this contract's Outputs section. No send_sms.py change, no new third-party dependency, no test-suite execution by the programmer, and no other file creation beyond the contract's stated Outputs.",
      "reviews": [
        {
          "point": 1,
          "status": "APPROVED",
          "review": "main.py line 121: `def main(argv: Sequence[str] | None = None) -> int`; line 123: `args = parser.parse_args(argv)`. `Sequence` was already imported (line 7). Lines 194-195 `if __name__ == \"__main__\": raise SystemExit(main())` are byte-for-byte unchanged. Full-file read confirms no other line was touched. Matches the point's acceptance criteria exactly."
        },
        {
          "point": 2,
          "status": "APPROVED",
          "review": "test_main.py's BuildParserTests (18 tests) covers all six subcommands. Defaults verified against actual main.py: send-batch/supplement batch_size=10, pause_seconds=45.0; find-sheet pause_seconds=20.0; dry_run=False, continue_on_error=False, timeout=DEFAULT_SEND_TIMEOUT everywhere it applies — all match the real build_parser() code read directly. --timeout override tests present for send/send-batch/supplement/find-one/find-sheet. duplicates' parser correctly has no --timeout attribute (test_duplicates_defaults asserts `not hasattr(args, 'timeout')`) and test_duplicates_rejects_timeout confirms passing --timeout raises SystemExit (argparse unrecognized-argument error), matching the real duplicates_parser which only defines --gate. Required-field omission tests (phone/message, gate, gate+number) all correctly wrapped in redirect_stderr and assertRaises(SystemExit), consistent with argparse's required=True behavior."
        },
        {
          "point": 3,
          "status": "APPROVED",
          "review": "MainDispatchTests (17 tests) patches each of the six imported send_sms functions via patch.object(main, ...) and invokes exclusively through the `_run_main` helper which calls `main.main(argv)` — never mutates sys.argv, never calls an unmocked send_sms function. Cross-checked every mock.assert_called_once_with(...) against main.py's actual call sites (e.g. poslat_davkove_sms's stop_on_error=not args.continue_on_error, config_path=args.config, timeout=args.timeout — all keyword names and positional gate argument match exactly) and against send_sms.py's real function signatures (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore, najit_duplikaty all confirmed keyword-only after the required positional args, matching test call shapes). send/send-batch/supplement/find-one/find-sheet each have an ok=True->0 and ok=False->1 test. duplicates has two tests (non-empty and empty list) both asserting return 0, matching main.py's duplicates branch which never checks 'ok'. Three tests (ConfigurationError, SpreadsheetError, ValueError) each confirm exit code 2, matching main.py's except clause exactly."
        },
        {
          "point": 4,
          "status": "APPROVED",
          "review": "streamlit_app.py: the module-level st.set_page_config() call no longer appears between imports and inject_styles() (confirmed by reading the full file top to bottom). Lines 810-815 now read `if __name__ == \"__main__\": st.set_page_config(page_title=\"Sprava GSM zavor\", layout=\"wide\"); main()` — set_page_config immediately followed by main(), in that order. A full-file read confirms every other `st.*` call lives inside a function body (inject_styles, load_config_cached, render_hero, run_messages_ui, render_sheet_health, render_flash_message, render_sheet_editor, main) or this guard — no other bare module-level Streamlit statement exists. No function body, argument, or other behavior was altered."
        },
        {
          "point": 5,
          "status": "APPROVED",
          "review": "test_streamlit_app.py imports `streamlit_app` directly (safe post-Point-4) plus GateConfig/SheetAnalysis/SheetRow/SmsResult from send_sms, whose field names (id/phone/password/sheet; row_number/raw_value/normalized/status/error; ok/phone/message/status_code/payload/error) were verified against the actual dataclass definitions in send_sms.py and match exactly. gate_label test asserts '3: 3 - Namesti' matching the real f'{gate.id}: {gate.sheet}' implementation. rows_dataframe test asserts the exact column list (radek, puvodni_hodnota, normalizovane_cislo, stav, chyba) against a 4-row fixture (valid/duplicate/invalid/blank) and a statuses filter test correctly returns only 2 rows. editable_numbers_dataframe test asserts a single 'telefon' column of 3 values (blank excluded), using normalized where present and raw for the invalid row, matching `row.normalized or row.raw_value for row in analysis.rows if row.status != 'blank'`. messages_dataframe test asserts 1-based poradi and matching prikaz_sms values. results_dataframe test asserts the exact column list (ok, telefon, zprava, status_code, chyba, odpoved), a payload correctly serialized via json.dumps into 'odpoved', and an errored/no-payload result yielding odpoved=''."
        },
        {
          "point": 6,
          "status": "APPROVED",
          "review": "README.md's 'Current limitations' no longer contains the original 'No automated tests exist for main.py ... or for streamlit_app.py' bullet. 'Current capabilities (v0.1)' gained two new bullets describing exactly what test_main.py and test_streamlit_app.py cover, matching the actual test content verified above. 'Current limitations' gained a new, narrower bullet naming streamlit_app.py's Streamlit-dependent rendering/interaction code (tabs, forms, session-state handling, widgets, main()) as untested and deferred. The pre-existing stale-lock-recovery limitation bullet is present and unaltered. No other README section (Purpose, Development environment, Planned evolution) was modified. The pre-existing '8 tests' text on the test_send_sms.py bullet was correctly left untouched, consistent with this being outside this contract's scope (already noted as such in the accepted Architecture Review)."
        }
      ]
    }
  ]
}
CONTRACT-META -->
