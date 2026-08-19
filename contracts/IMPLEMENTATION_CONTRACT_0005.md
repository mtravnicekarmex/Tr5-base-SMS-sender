# IMPLEMENTATION_CONTRACT_0005

Status: READY_FOR_PROGRAMMER

---

# Workflow

- Created by: `architect`
- Reviewer (both review gates): `reviewer`
- Implementer: `programmer`
- Risk level: `standard`
- Currently with: `programmer`
- Handed off to: `programmer`
- Created at: `2026-08-19T07:16:34+02:00`
- Updated at: `2026-08-19T07:17:47+02:00`

---

# Title

Make the gate sheet's phone-number column configurable per gate

---

# Purpose

Real gate sheets in the shared Excel workbook are not guaranteed to share an identical column layout, yet today's single global GATE_PHONE_COLUMN_INDEX constant is applied uniformly to every configured gate across ADD, FIND, and duplicate-detection operations. If a gate's real sheet ever has phone numbers in a different column, the application silently reads the wrong column with no way to correct it short of editing source code — for data that controls physical gate access, a silent wrong-column read is a real correctness risk, not a cosmetic one. Making the column configurable per gate, through the same config.toml mechanism already used for each gate's phone/password/sheet, closes this gap without inventing a new configuration channel.

---

# Intent

This is additive and backward compatible: a config.toml without the new field behaves exactly as today, since the new field's default equals the existing hardcoded constant's value. Scope is limited to the three send_sms.py functions and the two streamlit_app.py call sites that currently reference the global GATE_PHONE_COLUMN_INDEX constant for a gate's own sheet; SUPPLEMENT_PHONE_COLUMN_INDEX and the separate, single 'Doplnit' sheet it addresses are untouched, since that sheet is not per-gate and this problem does not apply to it. This does not add a Streamlit UI control for editing the column setting — config.toml remains the single source of truth for it, consistent with how each gate's phone/password/sheet already work; a UI control could be a later, separate addition if it turns out to be needed. It also keeps project/README.md and project/config.example.toml accurate and illustrative once this lands, matching the documentation discipline the prior contracts in this series have followed.

---

# Current State

project/send_sms.py defines GATE_PHONE_COLUMN_INDEX = 1 (module-level constant, 0-based column index, currently column B) and SUPPLEMENT_PHONE_COLUMN_INDEX = 0 (separate constant for the fixed 'Doplnit' sheet, unaffected by this change). GateConfig is a frozen dataclass with fields id, phone, password, sheet — no column-related field today. load_config() parses each [[gates]] TOML entry's id/phone/password/sheet with no handling of any column setting. GATE_PHONE_COLUMN_INDEX is passed as column_index directly in three send_sms.py functions: poslat_davkove_sms, najit_cisla_ze_seznamu_na_zavore, and najit_duplikaty (each calling get_sheet_numbers(active_config, gate.sheet, column_index=GATE_PHONE_COLUMN_INDEX, ...)). project/streamlit_app.py imports GATE_PHONE_COLUMN_INDEX from send_sms (its only three occurrences in the file: the import at line 14, a load_analysis_cached(config_path, selected_gate.sheet, GATE_PHONE_COLUMN_INDEX) call around line 497, and a render_sheet_editor(..., column_index=GATE_PHONE_COLUMN_INDEX, ...) call for the active gate's editor tab around line 559) — nothing else in streamlit_app.py references the constant. project/config.example.toml currently defines two example gates (id 1 'Benesovska', id 2 'Liberecka'), neither with any column-related field. project/README.md's 'Current limitations' section (most recently updated by IMPLEMENTATION_CONTRACT_0004) contains the bullet 'The phone number column layout is assumed uniform across all configured gate sheets, via a single global column-index constant.' project/tests/test_send_sms.py has one existing load_config test, test_load_config_reads_gate_definitions, using a temporary config.toml built inline.

---

# Inputs

The existing GateConfig dataclass and load_config() function in project/send_sms.py; the existing GATE_PHONE_COLUMN_INDEX module constant as the default fallback value; the three existing send_sms.py call sites (poslat_davkove_sms, najit_cisla_ze_seznamu_na_zavore, najit_duplikaty) and the two existing streamlit_app.py call sites that currently use the global constant; project/config.example.toml's existing two-gate structure; project/README.md's current 'Current capabilities (v0.1)' and 'Current limitations' sections; project/tests/test_send_sms.py's existing tempfile-based config.toml test pattern.

---

# Outputs

Modified project/send_sms.py: GateConfig gains a phone_column_index field (defaulting to GATE_PHONE_COLUMN_INDEX), load_config() parses an optional 'phone_column_index' key per gate with validation, and poslat_davkove_sms/najit_cisla_ze_seznamu_na_zavore/najit_duplikaty read column_index from the gate's own phone_column_index. Modified project/streamlit_app.py: both call sites use selected_gate.phone_column_index, and the now-unused GATE_PHONE_COLUMN_INDEX import is removed. Modified project/tests/test_send_sms.py: two new unit tests. Modified project/config.example.toml: one example gate illustrates the new optional field. Modified project/README.md: the resolved limitation moved into 'Current capabilities (v0.1)'. No other file is created or modified.

---

# Functional Requirements

## Point 1

SHALL: Add a phone_column_index field to the GateConfig dataclass in project/send_sms.py, defaulting to the existing GATE_PHONE_COLUMN_INDEX module constant.

Acceptance criteria:
- GateConfig gains a new field `phone_column_index: int = GATE_PHONE_COLUMN_INDEX`, added after the existing id/phone/password/sheet fields
- The dataclass remains frozen (`@dataclass(frozen=True)`) with no other field added, removed, or reordered

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 2

SHALL: Update load_config() in project/send_sms.py to parse an optional 'phone_column_index' key from each [[gates]] TOML entry, defaulting to GATE_PHONE_COLUMN_INDEX when the key is absent, and validating that the resolved value is a non-negative integer.

Acceptance criteria:
- When a gate's TOML entry omits 'phone_column_index', the resulting GateConfig.phone_column_index equals GATE_PHONE_COLUMN_INDEX
- When a gate's TOML entry includes 'phone_column_index' as a valid non-negative integer, the resulting GateConfig.phone_column_index equals that value
- When a gate's TOML entry includes 'phone_column_index' as a negative integer or a value that cannot be interpreted as an integer, load_config() raises ConfigurationError naming the offending gate
- No existing validation or error behavior for id/phone/password/sheet is altered

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 3

SHALL: Update poslat_davkove_sms, najit_cisla_ze_seznamu_na_zavore, and najit_duplikaty in project/send_sms.py to pass column_index=gate.phone_column_index to get_sheet_numbers instead of the global GATE_PHONE_COLUMN_INDEX constant.

Acceptance criteria:
- poslat_davkove_sms's get_sheet_numbers call uses column_index=gate.phone_column_index
- najit_cisla_ze_seznamu_na_zavore's get_sheet_numbers call uses column_index=gate.phone_column_index
- najit_duplikaty's get_sheet_numbers call uses column_index=gate.phone_column_index
- doplneni_seznamu_zavor's call (which uses SUPPLEMENT_PHONE_COLUMN_INDEX and SUPPLEMENT_SHEET_NAME, not a gate's own sheet) is left unchanged
- The GATE_PHONE_COLUMN_INDEX module constant itself is not removed (it remains GateConfig's default value, per the previous point)

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 4

SHALL: Update project/streamlit_app.py's two usages of the global GATE_PHONE_COLUMN_INDEX constant to use selected_gate.phone_column_index instead, and remove the now-unused GATE_PHONE_COLUMN_INDEX import if nothing else in the file references it.

Acceptance criteria:
- The load_analysis_cached(config_path, selected_gate.sheet, GATE_PHONE_COLUMN_INDEX) call is changed to pass selected_gate.phone_column_index
- The render_sheet_editor(..., column_index=GATE_PHONE_COLUMN_INDEX, ...) call for the active gate's editor tab is changed to pass column_index=selected_gate.phone_column_index
- GATE_PHONE_COLUMN_INDEX no longer appears anywhere in project/streamlit_app.py, including its import from send_sms
- SUPPLEMENT_PHONE_COLUMN_INDEX's import and its existing usage for the 'Doplnit' sheet tab are unchanged

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 5

SHALL: Add two new unit tests to project/tests/test_send_sms.py verifying load_config()'s new phone_column_index behavior, following the existing tempfile-based config.toml test pattern used by test_load_config_reads_gate_definitions.

Acceptance criteria:
- A new test builds a temporary config.toml whose gate entry omits 'phone_column_index' and asserts the loaded GateConfig's phone_column_index equals the imported GATE_PHONE_COLUMN_INDEX constant
- A second new test builds a temporary config.toml whose gate entry includes an explicit 'phone_column_index' value different from GATE_PHONE_COLUMN_INDEX (e.g. 3) and asserts the loaded GateConfig's phone_column_index equals that explicit value
- Both tests follow the existing tempfile.TemporaryDirectory()-based config.toml fixture pattern already used by test_load_config_reads_gate_definitions, not a mocked filesystem
- Actually executing the full test suite (13 tests total after this addition) and confirming all pass is an explicit manual follow-up for the owner, per this contract's Out of Scope, since the programmer has no Bash access to run it

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 6

SHALL: Update project/config.example.toml to illustrate the new optional phone_column_index field on one of the two example gates, leaving the other gate without it to show both the default and the override.

Acceptance criteria:
- Exactly one of the two example [[gates]] entries gains a 'phone_column_index' line with an explicit integer value
- The other example gate entry is left without a 'phone_column_index' line, demonstrating the default-when-omitted behavior
- No other field of either example gate (id, phone, password, sheet) or the top-level gateway_base/excel_path is changed

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 7

SHALL: Update project/README.md to move the resolved 'phone number column layout is assumed uniform across all configured gate sheets' bullet out of 'Current limitations' into 'Current capabilities (v0.1)', rephrased to describe the new per-gate configurability.

Acceptance criteria:
- The 'Current limitations' section no longer contains the 'phone number column layout is assumed uniform' bullet (or equivalent wording)
- The 'Current capabilities (v0.1)' section contains a new bullet or clause stating that each gate's phone-number column is configurable via an optional phone_column_index field in config.toml, defaulting to the prior hardcoded value when omitted
- The remaining 'Current limitations' bullets (missing tests for main.py/streamlit_app.py, stale-lock recovery) remain present and unaltered
- No other section of project/README.md is modified

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

---

# Out of Scope

This contract SHALL NOT change SUPPLEMENT_PHONE_COLUMN_INDEX or any handling of the 'Doplnit' sheet — that sheet is not per-gate and this problem does not apply to it. It SHALL NOT add a Streamlit UI control for editing phone_column_index — config.toml remains the sole configuration channel for it. It SHALL NOT modify project/main.py — none of its subcommands reference GATE_PHONE_COLUMN_INDEX directly; they call the already-updated send_sms.py functions. It SHALL NOT execute the test suite as part of the programmer's own verification — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash access to run `python -m unittest`/pytest; the programmer instead verifies the two new tests by reading and tracing their logic against the implementation, and actually running the full suite (13 tests after this addition) to confirm they pass is a manual follow-up for the owner after this contract is committed, per the established IMPLEMENTATION_CONTRACT_0002/0003 precedent. It SHALL NOT modify any section of project/README.md other than moving the one named bullet between 'Current limitations' and 'Current capabilities (v0.1)'.

---

# Acceptance Criteria

Acceptance criteria are listed per point in the Functional Requirements section.

---

# Architecture Review

### Round 1 — 2026-08-19T07:17:47+02:00 — Verdict: ACCEPTED — Reviewer: `reviewer`

Verified the contract's factual claims directly against project/send_sms.py, project/streamlit_app.py, project/config.example.toml, project/README.md, project/tests/test_send_sms.py, and project/main.py. All 'Current State' assertions checked out exactly: GATE_PHONE_COLUMN_INDEX = 1 and SUPPLEMENT_PHONE_COLUMN_INDEX = 0 as module constants; GateConfig is a frozen dataclass with exactly id/phone/password/sheet; load_config() parses only those four fields with no column handling; the three named functions (poslat_davkove_sms, najit_cisla_ze_seznamu_na_zavore, najit_duplikaty) pass column_index=GATE_PHONE_COLUMN_INDEX while doplneni_seznamu_zavor correctly uses SUPPLEMENT_PHONE_COLUMN_INDEX/SUPPLEMENT_SHEET_NAME instead; streamlit_app.py's three occurrences of GATE_PHONE_COLUMN_INDEX are exactly at the import (line 14) and the two call sites cited (lines 497 and 559); config.example.toml has exactly two gates with no column field; README.md's 'Current limitations' contains the cited bullet verbatim, and its own 'Planned evolution' section already lists 'per-gate column configuration' as a deferred item, confirming this is a documented, pre-existing gap being resolved rather than an invented need (satisfies P1/P15 — not a premature abstraction); main.py has zero references to GATE_PHONE_COLUMN_INDEX, confirming the Out of Scope claim about it. Counted existing tests in test_send_sms.py: 11, so the contract's 'defaulting to GATE_PHONE_COLUMN_INDEX... 13 tests total after this addition' (11+2) is arithmetically correct.

Checked against AGENTS.md: all Outputs are confined to project/ (send_sms.py, streamlit_app.py, tests/test_send_sms.py, config.example.toml, README.md) — no framework layer (agents/*.py, chat_architect.py) or governance .md file is touched, matching the project/-scoping rule (ADR-022) without needing an explicit contract point for anything outside project/. Backward compatibility is explicit and correct: the new field's default equals the existing hardcoded constant, so an unmodified config.toml behaves identically — no unjustified break. Out of Scope explicitly excludes SUPPLEMENT_PHONE_COLUMN_INDEX/'Doplnit' sheet, a Streamlit UI control, main.py, and test execution (correctly citing the programmer's 'edit' permission profile has no Bash access, consistent with IMPLEMENTATION_CONTRACT_0002/0003 precedent per the project's own established pattern) — no destructive commands or access beyond 'edit' are required anywhere in the seven points. No new file/directory names are proposed, so the naming-convention check is not applicable.

Each of the 7 points has an actionable, independently verifiable acceptance criterion, in a sensible dependency order (dataclass field -> config parsing -> call-site updates -> UI call-site updates -> tests -> example config -> docs). Point 2's validation criteria (non-negative integer, ConfigurationError naming the offending gate on a negative or non-integer value) is unambiguous enough to implement without further architectural decisions, consistent with the existing int(gate['id']) pattern already in load_config().

Risk-level check (Tr5-base decision 7): this change touches only config-schema parsing and internal call sites — no real credentials/API keys are introduced or altered, no new external-system calls, no native/hardware libraries, and no risk of landing personal/real data in git (config.toml itself stays gitignored, unchanged by this contract). 'standard' risk_level is correctly assigned; no escalation warranted.

No defects found. Contract may proceed to the programmer as written.

---

# Future Evolution

A Streamlit UI control for viewing/editing a gate's phone_column_index (instead of editing config.toml by hand) is a candidate for a later, separate contract if it turns out to be needed in practice, not designed now (P1/P15). The remaining limitation documented in project/README.md (stale-lock recovery; no automated tests for main.py/streamlit_app.py) stays deferred to its own future contract, untouched by this change.

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
  "number": 5,
  "title": "Make the gate sheet's phone-number column configurable per gate",
  "status": "READY_FOR_PROGRAMMER",
  "created_by": "architect",
  "assigned_to": "programmer",
  "handoff_to": "programmer",
  "created_at": "2026-08-19T07:16:34+02:00",
  "updated_at": "2026-08-19T07:17:47+02:00",
  "points": [
    {
      "number": 1,
      "assignment": "Add a phone_column_index field to the GateConfig dataclass in project/send_sms.py, defaulting to the existing GATE_PHONE_COLUMN_INDEX module constant.",
      "acceptance_criteria": [
        "GateConfig gains a new field `phone_column_index: int = GATE_PHONE_COLUMN_INDEX`, added after the existing id/phone/password/sheet fields",
        "The dataclass remains frozen (`@dataclass(frozen=True)`) with no other field added, removed, or reordered"
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
      "assignment": "Update load_config() in project/send_sms.py to parse an optional 'phone_column_index' key from each [[gates]] TOML entry, defaulting to GATE_PHONE_COLUMN_INDEX when the key is absent, and validating that the resolved value is a non-negative integer.",
      "acceptance_criteria": [
        "When a gate's TOML entry omits 'phone_column_index', the resulting GateConfig.phone_column_index equals GATE_PHONE_COLUMN_INDEX",
        "When a gate's TOML entry includes 'phone_column_index' as a valid non-negative integer, the resulting GateConfig.phone_column_index equals that value",
        "When a gate's TOML entry includes 'phone_column_index' as a negative integer or a value that cannot be interpreted as an integer, load_config() raises ConfigurationError naming the offending gate",
        "No existing validation or error behavior for id/phone/password/sheet is altered"
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
      "assignment": "Update poslat_davkove_sms, najit_cisla_ze_seznamu_na_zavore, and najit_duplikaty in project/send_sms.py to pass column_index=gate.phone_column_index to get_sheet_numbers instead of the global GATE_PHONE_COLUMN_INDEX constant.",
      "acceptance_criteria": [
        "poslat_davkove_sms's get_sheet_numbers call uses column_index=gate.phone_column_index",
        "najit_cisla_ze_seznamu_na_zavore's get_sheet_numbers call uses column_index=gate.phone_column_index",
        "najit_duplikaty's get_sheet_numbers call uses column_index=gate.phone_column_index",
        "doplneni_seznamu_zavor's call (which uses SUPPLEMENT_PHONE_COLUMN_INDEX and SUPPLEMENT_SHEET_NAME, not a gate's own sheet) is left unchanged",
        "The GATE_PHONE_COLUMN_INDEX module constant itself is not removed (it remains GateConfig's default value, per the previous point)"
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
      "assignment": "Update project/streamlit_app.py's two usages of the global GATE_PHONE_COLUMN_INDEX constant to use selected_gate.phone_column_index instead, and remove the now-unused GATE_PHONE_COLUMN_INDEX import if nothing else in the file references it.",
      "acceptance_criteria": [
        "The load_analysis_cached(config_path, selected_gate.sheet, GATE_PHONE_COLUMN_INDEX) call is changed to pass selected_gate.phone_column_index",
        "The render_sheet_editor(..., column_index=GATE_PHONE_COLUMN_INDEX, ...) call for the active gate's editor tab is changed to pass column_index=selected_gate.phone_column_index",
        "GATE_PHONE_COLUMN_INDEX no longer appears anywhere in project/streamlit_app.py, including its import from send_sms",
        "SUPPLEMENT_PHONE_COLUMN_INDEX's import and its existing usage for the 'Doplnit' sheet tab are unchanged"
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
      "assignment": "Add two new unit tests to project/tests/test_send_sms.py verifying load_config()'s new phone_column_index behavior, following the existing tempfile-based config.toml test pattern used by test_load_config_reads_gate_definitions.",
      "acceptance_criteria": [
        "A new test builds a temporary config.toml whose gate entry omits 'phone_column_index' and asserts the loaded GateConfig's phone_column_index equals the imported GATE_PHONE_COLUMN_INDEX constant",
        "A second new test builds a temporary config.toml whose gate entry includes an explicit 'phone_column_index' value different from GATE_PHONE_COLUMN_INDEX (e.g. 3) and asserts the loaded GateConfig's phone_column_index equals that explicit value",
        "Both tests follow the existing tempfile.TemporaryDirectory()-based config.toml fixture pattern already used by test_load_config_reads_gate_definitions, not a mocked filesystem",
        "Actually executing the full test suite (13 tests total after this addition) and confirming all pass is an explicit manual follow-up for the owner, per this contract's Out of Scope, since the programmer has no Bash access to run it"
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
      "assignment": "Update project/config.example.toml to illustrate the new optional phone_column_index field on one of the two example gates, leaving the other gate without it to show both the default and the override.",
      "acceptance_criteria": [
        "Exactly one of the two example [[gates]] entries gains a 'phone_column_index' line with an explicit integer value",
        "The other example gate entry is left without a 'phone_column_index' line, demonstrating the default-when-omitted behavior",
        "No other field of either example gate (id, phone, password, sheet) or the top-level gateway_base/excel_path is changed"
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
      "number": 7,
      "assignment": "Update project/README.md to move the resolved 'phone number column layout is assumed uniform across all configured gate sheets' bullet out of 'Current limitations' into 'Current capabilities (v0.1)', rephrased to describe the new per-gate configurability.",
      "acceptance_criteria": [
        "The 'Current limitations' section no longer contains the 'phone number column layout is assumed uniform' bullet (or equivalent wording)",
        "The 'Current capabilities (v0.1)' section contains a new bullet or clause stating that each gate's phone-number column is configurable via an optional phone_column_index field in config.toml, defaulting to the prior hardcoded value when omitted",
        "The remaining 'Current limitations' bullets (missing tests for main.py/streamlit_app.py, stale-lock recovery) remain present and unaltered",
        "No other section of project/README.md is modified"
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
  "purpose": "Real gate sheets in the shared Excel workbook are not guaranteed to share an identical column layout, yet today's single global GATE_PHONE_COLUMN_INDEX constant is applied uniformly to every configured gate across ADD, FIND, and duplicate-detection operations. If a gate's real sheet ever has phone numbers in a different column, the application silently reads the wrong column with no way to correct it short of editing source code — for data that controls physical gate access, a silent wrong-column read is a real correctness risk, not a cosmetic one. Making the column configurable per gate, through the same config.toml mechanism already used for each gate's phone/password/sheet, closes this gap without inventing a new configuration channel.",
  "intent": "This is additive and backward compatible: a config.toml without the new field behaves exactly as today, since the new field's default equals the existing hardcoded constant's value. Scope is limited to the three send_sms.py functions and the two streamlit_app.py call sites that currently reference the global GATE_PHONE_COLUMN_INDEX constant for a gate's own sheet; SUPPLEMENT_PHONE_COLUMN_INDEX and the separate, single 'Doplnit' sheet it addresses are untouched, since that sheet is not per-gate and this problem does not apply to it. This does not add a Streamlit UI control for editing the column setting — config.toml remains the single source of truth for it, consistent with how each gate's phone/password/sheet already work; a UI control could be a later, separate addition if it turns out to be needed. It also keeps project/README.md and project/config.example.toml accurate and illustrative once this lands, matching the documentation discipline the prior contracts in this series have followed.",
  "current_state": "project/send_sms.py defines GATE_PHONE_COLUMN_INDEX = 1 (module-level constant, 0-based column index, currently column B) and SUPPLEMENT_PHONE_COLUMN_INDEX = 0 (separate constant for the fixed 'Doplnit' sheet, unaffected by this change). GateConfig is a frozen dataclass with fields id, phone, password, sheet — no column-related field today. load_config() parses each [[gates]] TOML entry's id/phone/password/sheet with no handling of any column setting. GATE_PHONE_COLUMN_INDEX is passed as column_index directly in three send_sms.py functions: poslat_davkove_sms, najit_cisla_ze_seznamu_na_zavore, and najit_duplikaty (each calling get_sheet_numbers(active_config, gate.sheet, column_index=GATE_PHONE_COLUMN_INDEX, ...)). project/streamlit_app.py imports GATE_PHONE_COLUMN_INDEX from send_sms (its only three occurrences in the file: the import at line 14, a load_analysis_cached(config_path, selected_gate.sheet, GATE_PHONE_COLUMN_INDEX) call around line 497, and a render_sheet_editor(..., column_index=GATE_PHONE_COLUMN_INDEX, ...) call for the active gate's editor tab around line 559) — nothing else in streamlit_app.py references the constant. project/config.example.toml currently defines two example gates (id 1 'Benesovska', id 2 'Liberecka'), neither with any column-related field. project/README.md's 'Current limitations' section (most recently updated by IMPLEMENTATION_CONTRACT_0004) contains the bullet 'The phone number column layout is assumed uniform across all configured gate sheets, via a single global column-index constant.' project/tests/test_send_sms.py has one existing load_config test, test_load_config_reads_gate_definitions, using a temporary config.toml built inline.",
  "inputs": "The existing GateConfig dataclass and load_config() function in project/send_sms.py; the existing GATE_PHONE_COLUMN_INDEX module constant as the default fallback value; the three existing send_sms.py call sites (poslat_davkove_sms, najit_cisla_ze_seznamu_na_zavore, najit_duplikaty) and the two existing streamlit_app.py call sites that currently use the global constant; project/config.example.toml's existing two-gate structure; project/README.md's current 'Current capabilities (v0.1)' and 'Current limitations' sections; project/tests/test_send_sms.py's existing tempfile-based config.toml test pattern.",
  "outputs": "Modified project/send_sms.py: GateConfig gains a phone_column_index field (defaulting to GATE_PHONE_COLUMN_INDEX), load_config() parses an optional 'phone_column_index' key per gate with validation, and poslat_davkove_sms/najit_cisla_ze_seznamu_na_zavore/najit_duplikaty read column_index from the gate's own phone_column_index. Modified project/streamlit_app.py: both call sites use selected_gate.phone_column_index, and the now-unused GATE_PHONE_COLUMN_INDEX import is removed. Modified project/tests/test_send_sms.py: two new unit tests. Modified project/config.example.toml: one example gate illustrates the new optional field. Modified project/README.md: the resolved limitation moved into 'Current capabilities (v0.1)'. No other file is created or modified.",
  "out_of_scope": "This contract SHALL NOT change SUPPLEMENT_PHONE_COLUMN_INDEX or any handling of the 'Doplnit' sheet — that sheet is not per-gate and this problem does not apply to it. It SHALL NOT add a Streamlit UI control for editing phone_column_index — config.toml remains the sole configuration channel for it. It SHALL NOT modify project/main.py — none of its subcommands reference GATE_PHONE_COLUMN_INDEX directly; they call the already-updated send_sms.py functions. It SHALL NOT execute the test suite as part of the programmer's own verification — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash access to run `python -m unittest`/pytest; the programmer instead verifies the two new tests by reading and tracing their logic against the implementation, and actually running the full suite (13 tests after this addition) to confirm they pass is a manual follow-up for the owner after this contract is committed, per the established IMPLEMENTATION_CONTRACT_0002/0003 precedent. It SHALL NOT modify any section of project/README.md other than moving the one named bullet between 'Current limitations' and 'Current capabilities (v0.1)'.",
  "future_evolution": "A Streamlit UI control for viewing/editing a gate's phone_column_index (instead of editing config.toml by hand) is a candidate for a later, separate contract if it turns out to be needed in practice, not designed now (P1/P15). The remaining limitation documented in project/README.md (stale-lock recovery; no automated tests for main.py/streamlit_app.py) stays deferred to its own future contract, untouched by this change.",
  "lessons_learned": "",
  "architecture_review_rounds": [
    {
      "round": 1,
      "date": "2026-08-19T07:17:47+02:00",
      "verdict": "ACCEPTED",
      "reviewer": "reviewer",
      "findings": "Verified the contract's factual claims directly against project/send_sms.py, project/streamlit_app.py, project/config.example.toml, project/README.md, project/tests/test_send_sms.py, and project/main.py. All 'Current State' assertions checked out exactly: GATE_PHONE_COLUMN_INDEX = 1 and SUPPLEMENT_PHONE_COLUMN_INDEX = 0 as module constants; GateConfig is a frozen dataclass with exactly id/phone/password/sheet; load_config() parses only those four fields with no column handling; the three named functions (poslat_davkove_sms, najit_cisla_ze_seznamu_na_zavore, najit_duplikaty) pass column_index=GATE_PHONE_COLUMN_INDEX while doplneni_seznamu_zavor correctly uses SUPPLEMENT_PHONE_COLUMN_INDEX/SUPPLEMENT_SHEET_NAME instead; streamlit_app.py's three occurrences of GATE_PHONE_COLUMN_INDEX are exactly at the import (line 14) and the two call sites cited (lines 497 and 559); config.example.toml has exactly two gates with no column field; README.md's 'Current limitations' contains the cited bullet verbatim, and its own 'Planned evolution' section already lists 'per-gate column configuration' as a deferred item, confirming this is a documented, pre-existing gap being resolved rather than an invented need (satisfies P1/P15 — not a premature abstraction); main.py has zero references to GATE_PHONE_COLUMN_INDEX, confirming the Out of Scope claim about it. Counted existing tests in test_send_sms.py: 11, so the contract's 'defaulting to GATE_PHONE_COLUMN_INDEX... 13 tests total after this addition' (11+2) is arithmetically correct.\n\nChecked against AGENTS.md: all Outputs are confined to project/ (send_sms.py, streamlit_app.py, tests/test_send_sms.py, config.example.toml, README.md) — no framework layer (agents/*.py, chat_architect.py) or governance .md file is touched, matching the project/-scoping rule (ADR-022) without needing an explicit contract point for anything outside project/. Backward compatibility is explicit and correct: the new field's default equals the existing hardcoded constant, so an unmodified config.toml behaves identically — no unjustified break. Out of Scope explicitly excludes SUPPLEMENT_PHONE_COLUMN_INDEX/'Doplnit' sheet, a Streamlit UI control, main.py, and test execution (correctly citing the programmer's 'edit' permission profile has no Bash access, consistent with IMPLEMENTATION_CONTRACT_0002/0003 precedent per the project's own established pattern) — no destructive commands or access beyond 'edit' are required anywhere in the seven points. No new file/directory names are proposed, so the naming-convention check is not applicable.\n\nEach of the 7 points has an actionable, independently verifiable acceptance criterion, in a sensible dependency order (dataclass field -> config parsing -> call-site updates -> UI call-site updates -> tests -> example config -> docs). Point 2's validation criteria (non-negative integer, ConfigurationError naming the offending gate on a negative or non-integer value) is unambiguous enough to implement without further architectural decisions, consistent with the existing int(gate['id']) pattern already in load_config().\n\nRisk-level check (Tr5-base decision 7): this change touches only config-schema parsing and internal call sites — no real credentials/API keys are introduced or altered, no new external-system calls, no native/hardware libraries, and no risk of landing personal/real data in git (config.toml itself stays gitignored, unchanged by this contract). 'standard' risk_level is correctly assigned; no escalation warranted.\n\nNo defects found. Contract may proceed to the programmer as written."
    }
  ],
  "completion_notes": "",
  "implementation_review_rounds": []
}
CONTRACT-META -->
