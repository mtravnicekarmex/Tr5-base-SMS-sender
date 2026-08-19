# IMPLEMENTATION_CONTRACT_0006

Status: READY_FOR_PROGRAMMER

---

# Workflow

- Created by: `architect`
- Reviewer (both review gates): `reviewer`
- Implementer: `programmer`
- Risk level: `standard`
- Currently with: `programmer`
- Handed off to: `programmer`
- Created at: `2026-08-19T14:41:41+02:00`
- Updated at: `2026-08-19T14:43:41+02:00`

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

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 2

SHALL: Add a new project/tests/test_main.py with unit tests for build_parser(), covering all six subcommands' arguments, types, defaults, and required flags, including the --timeout float argument (default send_sms.DEFAULT_SEND_TIMEOUT) present on send/send-batch/supplement/find-one/find-sheet and absent on duplicates.

Acceptance criteria:
- For each of the six subcommands, a test parses a minimal valid argument list (using build_parser().parse_args([...])) and asserts the parsed namespace has the expected attributes and default values (e.g. send-batch's default batch_size=10, pause_seconds=45.0, dry_run=False, continue_on_error=False, timeout=DEFAULT_SEND_TIMEOUT)
- A test confirms --timeout is accepted and correctly overrides the default on each of send, send-batch, supplement, find-one, and find-sheet
- A test confirms the duplicates subcommand's parser does not define a --timeout argument (parsing `duplicates --gate 1 --timeout 5` raises SystemExit/an argparse error)
- A test confirms each subcommand's required arguments (e.g. --phone/--message for send, --gate for the others, --number for find-one) raise SystemExit when omitted, consistent with argparse's required=True behavior

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 3

SHALL: Add unit tests to project/tests/test_main.py for main()'s dispatch logic, using unittest.mock.patch to replace each of the six send_sms functions imported into the main module's namespace, invoking main() via its new argv parameter with no real network or file I/O.

Acceptance criteria:
- For each of the six subcommands, at least one test patches the corresponding imported function (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore, or najit_duplikaty) in the main module's namespace, calls main(argv=[...]), and asserts the mock was called with arguments matching the parsed CLI flags
- For send, send-batch, supplement, find-one, and find-sheet, at least one test asserts main() returns 0 when the mocked function's result(s) indicate success (ok=True), and at least one test asserts main() returns 1 when they indicate failure (ok=False)
- For duplicates, a test asserts main() returns 0 regardless of the mocked najit_duplikaty's return value (a list), since that branch does not check an ok field
- At least one test asserts that when the mocked function raises ConfigurationError, SpreadsheetError, or ValueError, main() returns 2
- Every test in this point invokes main() through its argv parameter (not by mutating sys.argv) and never calls a real, unmocked send_sms function

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 4

SHALL: Relocate project/streamlit_app.py's module-level st.set_page_config(page_title="Sprava GSM zavor", layout="wide") call into the existing `if __name__ == "__main__":` guard, immediately before the call to main(), so the call no longer executes merely by importing the module.

Acceptance criteria:
- The st.set_page_config(...) call no longer appears at module level (outside any function or guard)
- The `if __name__ == "__main__":` block now contains the st.set_page_config(...) call immediately followed by the existing call to main(), in that order
- No other module-level statement in streamlit_app.py executes a Streamlit command outside a function body or this guard (confirmed by reading the full file)
- No function body, argument, or behavior elsewhere in streamlit_app.py is changed by this point

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 5

SHALL: Add a new project/tests/test_streamlit_app.py with unit tests for the pure helper functions gate_label, rows_dataframe, editable_numbers_dataframe, messages_dataframe, and results_dataframe, importing streamlit_app directly.

Acceptance criteria:
- The test file imports streamlit_app directly (e.g. `import streamlit_app` or `from streamlit_app import ...`) and, per the previous point's fix, this import does not execute st.set_page_config() or require a live Streamlit script context
- A test for gate_label asserts it returns the expected '<id>: <sheet>' string for a given GateConfig
- A test for rows_dataframe asserts the returned DataFrame has the expected columns (radek, puvodni_hodnota, normalizovane_cislo, stav, chyba) for a SheetAnalysis with a mix of valid/duplicate/invalid/blank rows, and that passing a `statuses` filter returns only matching rows
- A test for editable_numbers_dataframe asserts the returned DataFrame's 'telefon' column excludes blank rows and includes normalized (or raw, when not normalized) values for the rest
- A test for messages_dataframe asserts the returned DataFrame has 1-based 'poradi' values and a 'prikaz_sms' column matching the input message list
- A test for results_dataframe asserts the returned DataFrame's columns (ok, telefon, zprava, status_code, chyba, odpoved) match a given list of SmsResult objects, including one with a non-None payload serialized into 'odpoved'

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 6

SHALL: Update project/README.md: move the resolved portion of the 'No automated tests exist for main.py ... or for streamlit_app.py' limitation into 'Current capabilities (v0.1)' describing exactly what is now covered, and add a narrower residual limitation bullet stating that streamlit_app.py's Streamlit-dependent rendering/interaction code remains untested.

Acceptance criteria:
- The 'Current limitations' section no longer contains the original 'No automated tests exist for main.py ... or for streamlit_app.py' bullet
- The 'Current capabilities (v0.1)' section contains a new bullet or clause stating that main.py's argument parsing and dispatch logic, and streamlit_app.py's pure data-transformation helper functions, are now covered by automated tests
- The 'Current limitations' section contains a new, narrower bullet stating that streamlit_app.py's Streamlit-dependent rendering/interaction code (tabs, forms, session state, widgets, main()) remains untested, and that covering it is deferred to a possible future contract
- The other existing 'Current limitations' bullet (stale-lock recovery) remains present and unaltered, and no other section of project/README.md is modified

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

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
  "number": 6,
  "title": "Add automated test coverage for main.py and streamlit_app.py's pure helpers",
  "status": "READY_FOR_PROGRAMMER",
  "created_by": "architect",
  "assigned_to": "programmer",
  "handoff_to": "programmer",
  "created_at": "2026-08-19T14:41:41+02:00",
  "updated_at": "2026-08-19T14:43:41+02:00",
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
      "assignment": "Add a new project/tests/test_main.py with unit tests for build_parser(), covering all six subcommands' arguments, types, defaults, and required flags, including the --timeout float argument (default send_sms.DEFAULT_SEND_TIMEOUT) present on send/send-batch/supplement/find-one/find-sheet and absent on duplicates.",
      "acceptance_criteria": [
        "For each of the six subcommands, a test parses a minimal valid argument list (using build_parser().parse_args([...])) and asserts the parsed namespace has the expected attributes and default values (e.g. send-batch's default batch_size=10, pause_seconds=45.0, dry_run=False, continue_on_error=False, timeout=DEFAULT_SEND_TIMEOUT)",
        "A test confirms --timeout is accepted and correctly overrides the default on each of send, send-batch, supplement, find-one, and find-sheet",
        "A test confirms the duplicates subcommand's parser does not define a --timeout argument (parsing `duplicates --gate 1 --timeout 5` raises SystemExit/an argparse error)",
        "A test confirms each subcommand's required arguments (e.g. --phone/--message for send, --gate for the others, --number for find-one) raise SystemExit when omitted, consistent with argparse's required=True behavior"
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
      "assignment": "Add unit tests to project/tests/test_main.py for main()'s dispatch logic, using unittest.mock.patch to replace each of the six send_sms functions imported into the main module's namespace, invoking main() via its new argv parameter with no real network or file I/O.",
      "acceptance_criteria": [
        "For each of the six subcommands, at least one test patches the corresponding imported function (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore, or najit_duplikaty) in the main module's namespace, calls main(argv=[...]), and asserts the mock was called with arguments matching the parsed CLI flags",
        "For send, send-batch, supplement, find-one, and find-sheet, at least one test asserts main() returns 0 when the mocked function's result(s) indicate success (ok=True), and at least one test asserts main() returns 1 when they indicate failure (ok=False)",
        "For duplicates, a test asserts main() returns 0 regardless of the mocked najit_duplikaty's return value (a list), since that branch does not check an ok field",
        "At least one test asserts that when the mocked function raises ConfigurationError, SpreadsheetError, or ValueError, main() returns 2",
        "Every test in this point invokes main() through its argv parameter (not by mutating sys.argv) and never calls a real, unmocked send_sms function"
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
      "assignment": "Relocate project/streamlit_app.py's module-level st.set_page_config(page_title=\"Sprava GSM zavor\", layout=\"wide\") call into the existing `if __name__ == \"__main__\":` guard, immediately before the call to main(), so the call no longer executes merely by importing the module.",
      "acceptance_criteria": [
        "The st.set_page_config(...) call no longer appears at module level (outside any function or guard)",
        "The `if __name__ == \"__main__\":` block now contains the st.set_page_config(...) call immediately followed by the existing call to main(), in that order",
        "No other module-level statement in streamlit_app.py executes a Streamlit command outside a function body or this guard (confirmed by reading the full file)",
        "No function body, argument, or behavior elsewhere in streamlit_app.py is changed by this point"
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
      "assignment": "Add a new project/tests/test_streamlit_app.py with unit tests for the pure helper functions gate_label, rows_dataframe, editable_numbers_dataframe, messages_dataframe, and results_dataframe, importing streamlit_app directly.",
      "acceptance_criteria": [
        "The test file imports streamlit_app directly (e.g. `import streamlit_app` or `from streamlit_app import ...`) and, per the previous point's fix, this import does not execute st.set_page_config() or require a live Streamlit script context",
        "A test for gate_label asserts it returns the expected '<id>: <sheet>' string for a given GateConfig",
        "A test for rows_dataframe asserts the returned DataFrame has the expected columns (radek, puvodni_hodnota, normalizovane_cislo, stav, chyba) for a SheetAnalysis with a mix of valid/duplicate/invalid/blank rows, and that passing a `statuses` filter returns only matching rows",
        "A test for editable_numbers_dataframe asserts the returned DataFrame's 'telefon' column excludes blank rows and includes normalized (or raw, when not normalized) values for the rest",
        "A test for messages_dataframe asserts the returned DataFrame has 1-based 'poradi' values and a 'prikaz_sms' column matching the input message list",
        "A test for results_dataframe asserts the returned DataFrame's columns (ok, telefon, zprava, status_code, chyba, odpoved) match a given list of SmsResult objects, including one with a non-None payload serialized into 'odpoved'"
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
      "assignment": "Update project/README.md: move the resolved portion of the 'No automated tests exist for main.py ... or for streamlit_app.py' limitation into 'Current capabilities (v0.1)' describing exactly what is now covered, and add a narrower residual limitation bullet stating that streamlit_app.py's Streamlit-dependent rendering/interaction code remains untested.",
      "acceptance_criteria": [
        "The 'Current limitations' section no longer contains the original 'No automated tests exist for main.py ... or for streamlit_app.py' bullet",
        "The 'Current capabilities (v0.1)' section contains a new bullet or clause stating that main.py's argument parsing and dispatch logic, and streamlit_app.py's pure data-transformation helper functions, are now covered by automated tests",
        "The 'Current limitations' section contains a new, narrower bullet stating that streamlit_app.py's Streamlit-dependent rendering/interaction code (tabs, forms, session state, widgets, main()) remains untested, and that covering it is deferred to a possible future contract",
        "The other existing 'Current limitations' bullet (stale-lock recovery) remains present and unaltered, and no other section of project/README.md is modified"
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
  "completion_notes": "",
  "implementation_review_rounds": []
}
CONTRACT-META -->
