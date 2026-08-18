# IMPLEMENTATION_CONTRACT_0004

Status: READY_FOR_REVIEWER

---

# Workflow

- Created by: `architect`
- Reviewer (both review gates): `reviewer`
- Implementer: `programmer`
- Risk level: `standard`
- Currently with: `reviewer`
- Handed off to: `reviewer`
- Created at: `2026-08-18T15:29:30+02:00`
- Updated at: `2026-08-18T15:32:54+02:00`

---

# Title

Add --timeout CLI parity to main.py's SMS-sending subcommands

---

# Purpose

project/main.py has no way to configure the HTTP timeout used when talking to the SMS gateway — every SMS-sending subcommand silently falls back to send_sms.py's function-level default (DEFAULT_SEND_TIMEOUT, 10.0s), even though every one of those functions already accepts a timeout keyword argument. The Streamlit UI already exposes this per operation (a 'HTTP timeout [s]' number input in each form), so the CLI is inconsistent with it — someone operating the CLI over a slow or flaky gateway connection today has no way to raise the timeout without editing source. This closes that documented parity gap directly, at the smallest possible scope: one new optional flag, wired to a parameter that already exists.

---

# Intent

This is a purely additive change: one new --timeout argument on each of the five subcommands that actually send something over HTTP (send, send-batch, supplement, find-one, find-sheet), wired straight through to the existing timeout keyword each corresponding send_sms.py function already accepts. No function signature, default value, or behavior changes when the flag is omitted — the new argument's own default is send_sms.DEFAULT_SEND_TIMEOUT, exactly what every call already falls back to today, so omitting --timeout is fully backward-compatible. The duplicates subcommand is deliberately left untouched since it never sends anything over HTTP. This does not add any new automated test coverage for main.py itself — CLI argument-parsing tests for main.py are a separate, already-queued follow-up contract (project/README.md's 'no automated tests for main.py' limitation) and adding partial test infrastructure here would blur that boundary. It also updates project/README.md so the limitation it documents does not go stale the moment this lands, consistent with how every prior contract in this series has kept that file's 'Current limitations'/'Current capabilities' split accurate.

---

# Current State

project/main.py's build_parser() defines six subcommands via argparse: send (--phone, --message), send-batch (--gate, --batch-size, --pause-seconds, --dry-run, --continue-on-error), supplement (same shape as send-batch), find-one (--gate, --number, --dry-run), find-sheet (--gate, --pause-seconds, --dry-run, --continue-on-error), and duplicates (--gate only, lists duplicates without sending anything). None of the six subcommands currently defines a --timeout argument, and main() never passes a timeout= keyword to any of the send_sms.py functions it calls (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore) — each of those functions already has its own `timeout: float = DEFAULT_SEND_TIMEOUT` keyword parameter (DEFAULT_SEND_TIMEOUT = 10.0, defined in send_sms.py) that main.py simply never overrides. main.py's current import block pulls ConfigurationError, SpreadsheetError, doplneni_seznamu_zavor, najit_cisla_ze_seznamu_na_zavore, najit_cislo_na_zavore, najit_duplikaty, poslat_davkove_sms, poslat_sms from send_sms — DEFAULT_SEND_TIMEOUT is not currently imported into main.py. project/README.md's 'Current limitations' section (most recently updated by IMPLEMENTATION_CONTRACT_0003) currently contains the bullet 'CLI commands do not expose a `--timeout` option, unlike the Streamlit UI.' among four listed limitations.

---

# Inputs

The existing project/main.py build_parser() and main() functions; the existing timeout keyword parameters already present on poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, and najit_cisla_ze_seznamu_na_zavore in project/send_sms.py; DEFAULT_SEND_TIMEOUT's existing value in project/send_sms.py; project/README.md's current 'Current limitations' and 'Current capabilities (v0.1)' sections.

---

# Outputs

Modified project/main.py: a new --timeout float argument on the send, send-batch, supplement, find-one, and find-sheet subparsers (default send_sms.DEFAULT_SEND_TIMEOUT), and the parsed value passed as timeout=args.timeout to each corresponding send_sms.py function call in main(). Modified project/README.md: the 'CLI commands do not expose a --timeout option' bullet moved out of 'Current limitations' into 'Current capabilities (v0.1)'. No other file is created or modified.

---

# Functional Requirements

## Point 1

SHALL: Import DEFAULT_SEND_TIMEOUT from send_sms in project/main.py, and add a --timeout float argument (default DEFAULT_SEND_TIMEOUT) to each of the five subparsers that send something over HTTP: send, send-batch, supplement, find-one, find-sheet.

Acceptance criteria:
- project/main.py's import from send_sms includes DEFAULT_SEND_TIMEOUT alongside the existing imported names
- send_parser, batch_parser (send-batch), supplement_parser, find_one_parser, and find_sheet_parser each gain a `--timeout` argument with `type=float` and `default=DEFAULT_SEND_TIMEOUT`, with a help string describing it as the HTTP timeout for the gateway request in seconds
- duplicates_parser does not gain a --timeout argument
- No existing argument on any of the six subparsers (--phone, --message, --gate, --batch-size, --pause-seconds, --dry-run, --continue-on-error, --number, --config, --verbose) is removed, renamed, or has its default changed

> Status: IMPLEMENTED

Programmer note:

_By `programmer`, 2026-08-18T15:32:54+02:00._

Imported DEFAULT_SEND_TIMEOUT into project/main.py's existing `from send_sms import (...)` block (alongside ConfigurationError, SpreadsheetError, and the five functions). Added a `--timeout` argument (type=float, default=DEFAULT_SEND_TIMEOUT, help='HTTP timeout for the gateway request, in seconds.') to send_parser, batch_parser (send-batch), supplement_parser, find_one_parser, and find_sheet_parser. duplicates_parser was left unchanged with only --gate. No existing argument (--phone, --message, --gate, --batch-size, --pause-seconds, --dry-run, --continue-on-error, --number, --config, --verbose) was removed, renamed, or had its default altered.

Files touched:
- `project/main.py`

Tests:
- Manual read-through of project/main.py after edits: confirmed all five target subparsers gained --timeout (type=float, default=DEFAULT_SEND_TIMEOUT), duplicates_parser did not, and all five corresponding main() call sites pass timeout=args.timeout while the duplicates call site is unchanged.
- Manual read-through of project/send_sms.py: confirmed timeout is keyword-only with default DEFAULT_SEND_TIMEOUT (=10.0) on poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, and najit_cisla_ze_seznamu_na_zavore, and that najit_duplikaty has no timeout parameter.
- Manual read-through of project/README.md after edits: confirmed the --timeout bullet moved from 'Current limitations' into 'Current capabilities (v0.1)' and the other three limitations bullets are untouched.

Reviewer's implementation review for this point:

_Awaiting review._

## Point 2

SHALL: In main()'s command dispatch, pass the parsed timeout value through to the corresponding send_sms.py function call for each of the five subcommands touched by the previous point.

Acceptance criteria:
- The 'send' branch calls poslat_sms(..., timeout=args.timeout, ...)
- The 'send-batch' branch calls poslat_davkove_sms(..., timeout=args.timeout, ...)
- The 'supplement' branch calls doplneni_seznamu_zavor(..., timeout=args.timeout, ...)
- The 'find-one' branch calls najit_cislo_na_zavore(..., timeout=args.timeout, ...)
- The 'find-sheet' branch calls najit_cisla_ze_seznamu_na_zavore(..., timeout=args.timeout, ...)
- The 'duplicates' branch (najit_duplikaty call) is unchanged and receives no timeout argument
- Running main.py with no --timeout flag on any of the five subcommands produces the exact same effective timeout value as before this change (DEFAULT_SEND_TIMEOUT), verified by reading that the new default matches the value each function already fell back to

> Status: IMPLEMENTED

Programmer note:

_By `programmer`, 2026-08-18T15:32:54+02:00._

Updated main()'s five dispatch branches to pass timeout=args.timeout: poslat_sms (send), poslat_davkove_sms (send-batch), doplneni_seznamu_zavor (supplement), najit_cislo_na_zavore (find-one), and najit_cisla_ze_seznamu_na_zavore (find-sheet). The duplicates branch's najit_duplikaty(args.gate, config_path=args.config) call was left unchanged (that function has no timeout parameter). Verified by reading send_sms.py that timeout is a keyword-only parameter (after `*`) on all five target functions, each defaulting to DEFAULT_SEND_TIMEOUT (10.0), so the new CLI --timeout default is byte-for-byte identical to what each function already fell back to when the flag is omitted — no behavior change for existing callers. No automated test was run/added (none was in scope for this point; the contract's Intent explicitly excludes it and Point 2's own acceptance criterion is phrased as a read-time check).

Files touched:
- `project/main.py`

Tests:
- Manual read-through of project/main.py after edits: confirmed all five target subparsers gained --timeout (type=float, default=DEFAULT_SEND_TIMEOUT), duplicates_parser did not, and all five corresponding main() call sites pass timeout=args.timeout while the duplicates call site is unchanged.
- Manual read-through of project/send_sms.py: confirmed timeout is keyword-only with default DEFAULT_SEND_TIMEOUT (=10.0) on poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, and najit_cisla_ze_seznamu_na_zavore, and that najit_duplikaty has no timeout parameter.
- Manual read-through of project/README.md after edits: confirmed the --timeout bullet moved from 'Current limitations' into 'Current capabilities (v0.1)' and the other three limitations bullets are untouched.

Reviewer's implementation review for this point:

_Awaiting review._

## Point 3

SHALL: Update project/README.md to move the now-resolved 'CLI commands do not expose a --timeout option, unlike the Streamlit UI' bullet out of 'Current limitations' and into 'Current capabilities (v0.1)', rephrased to state the capability now exists.

Acceptance criteria:
- The 'Current limitations' section no longer contains the 'CLI commands do not expose a --timeout option' bullet (or equivalent wording)
- The 'Current capabilities (v0.1)' section contains a new bullet or clause stating that the CLI's SMS-sending subcommands now accept a --timeout option, matching the Streamlit UI
- The other three 'Current limitations' bullets (missing tests for main.py/streamlit_app.py, stale-lock recovery, single global phone-column-index assumption) remain present and unaltered
- No other section of project/README.md is modified

> Status: IMPLEMENTED

Programmer note:

_By `programmer`, 2026-08-18T15:32:54+02:00._

Removed the 'CLI commands do not expose a `--timeout` option, unlike the Streamlit UI.' bullet from README.md's 'Current limitations' section. Added a sentence to the existing `main.py` bullet in 'Current capabilities (v0.1)' stating the five SMS-sending subcommands now accept a --timeout option matching the Streamlit UI. The other three 'Current limitations' bullets (missing main.py/streamlit_app.py tests, stale-lock recovery, single global phone-column-index assumption) were left present and unaltered, and no other section of README.md was touched.

Files touched:
- `project/README.md`

Tests:
- Manual read-through of project/main.py after edits: confirmed all five target subparsers gained --timeout (type=float, default=DEFAULT_SEND_TIMEOUT), duplicates_parser did not, and all five corresponding main() call sites pass timeout=args.timeout while the duplicates call site is unchanged.
- Manual read-through of project/send_sms.py: confirmed timeout is keyword-only with default DEFAULT_SEND_TIMEOUT (=10.0) on poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, and najit_cisla_ze_seznamu_na_zavore, and that najit_duplikaty has no timeout parameter.
- Manual read-through of project/README.md after edits: confirmed the --timeout bullet moved from 'Current limitations' into 'Current capabilities (v0.1)' and the other three limitations bullets are untouched.

Reviewer's implementation review for this point:

_Awaiting review._

---

# Out of Scope

This contract SHALL NOT add a --timeout argument to the duplicates subcommand — it sends nothing over HTTP, so timeout does not apply to it. It SHALL NOT add any new automated test coverage for project/main.py (CLI argument-parsing/exit-code tests for main.py remain a separate, already-queued follow-up item). It SHALL NOT modify project/send_sms.py or project/streamlit_app.py — the timeout keyword parameters and DEFAULT_SEND_TIMEOUT this contract wires into already exist and are unchanged. It SHALL NOT change DEFAULT_SEND_TIMEOUT's value or any other subcommand's existing arguments/behavior. It SHALL NOT modify any section of project/README.md other than moving the one named bullet between 'Current limitations' and 'Current capabilities (v0.1)'.

---

# Acceptance Criteria

Acceptance criteria are listed per point in the Functional Requirements section.

---

# Architecture Review

### Round 1 — 2026-08-18T15:30:58+02:00 — Verdict: ACCEPTED — Reviewer: `reviewer`

Verified the contract's factual claims directly against project/main.py, project/send_sms.py, and project/README.md (per PRINCIPLES.md P7/P6 — Current State must be established from the actual code, not memory). Result: every claim in 'Current State' is accurate. build_parser() defines exactly the six subcommands and argument sets described, none currently has --timeout, and main() never passes timeout= to any send_sms.py call. All five target functions (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore) have a keyword-only `timeout: float = DEFAULT_SEND_TIMEOUT` parameter (DEFAULT_SEND_TIMEOUT = 10.0, defined at send_sms.py:26); najit_duplikaty has no timeout parameter, confirming duplicates is correctly excluded. main.py's current import statement indeed omits DEFAULT_SEND_TIMEOUT. project/README.md's 'Current limitations' section contains the exact bullet quoted in the contract ('CLI commands do not expose a `--timeout` option, unlike the Streamlit UI.'), and the other three limitations bullets named in Point 3's acceptance criteria (missing tests for main.py/streamlit_app.py, stale-lock recovery, single global phone-column-index assumption) are present and match.

Purpose/Intent check: this closes a real, already-documented gap (the README's own limitations bullet, added by CONTRACT_0003) rather than anticipating a future need — consistent with P1/P8. It is deliberately minimal (one flag, wired to an already-existing parameter), not a premature abstraction.

Points are actionable in stated order and each acceptance criterion is concretely verifiable by reading the diff (parser definitions, call-site keyword, README section membership) — none require guessing. Because every target function takes `timeout` as keyword-only (after `*`), `timeout=args.timeout` is unambiguous regardless of call-site argument order, so no implementation choice is left open. Point 2's 'produces the exact same effective timeout value... verified by reading' is explicitly a read-time check, not a new test, which matches the Intent's explicit statement that no automated test coverage is added here (deferred to the already-queued main.py test contract) — internally consistent, no contradiction.

Out of Scope explicitly addresses the main edge case (duplicates subcommand, which has no timeout parameter at all) and forecloses scope creep into send_sms.py, streamlit_app.py, DEFAULT_SEND_TIMEOUT's value, other subcommand args, and unrelated README sections — no ambiguity for the programmer to resolve.

Backward compatibility: explicitly preserved — new argument's own default equals the value every call already silently used, verified against the actual DEFAULT_SEND_TIMEOUT constant and each function's existing default; no signature or default changes to existing arguments. No violation.

Scope/permissions: only project/main.py and project/README.md are touched, both already inside project/ (AGENTS.md/ADR-022's default write scope — no framework or governance file touched, so no separate scope point was needed). No shell/git command is required by any point (per the CONTRACT_0002 architecture-review finding on record, the programmer's 'edit' permission profile has no Bash) — Point 2's verification step is explicitly satisfied by reading, not by running anything, so this contract is fully executable under the programmer's actual tool access.

Naming convention: no new file/directory is proposed, so ADR-008's convention does not apply here.

Risk level: checked against Tr5-base decision 7's criteria (real credentials/API keys, real calls to external systems, native/hardware libraries, risk of landing personal/real data in git). This contract adds no new external call, credential, or data-handling path — it only threads an existing timeout value through argparse to an existing keyword argument. 'standard' is the correct classification; no escalation warranted.

---

# Future Evolution

CLI argument-parsing test coverage for project/main.py (which would include a test asserting --timeout is parsed and defaulted correctly) is deferred to the already-queued, separate 'missing tests for main.py/streamlit_app.py' follow-up contract. The remaining limitations documented in project/README.md (per-gate phone-column configuration, stale-lock recovery) stay deferred to their own future contracts, untouched by this change.

---

# Completion Notes

Added --timeout float CLI argument to the five SMS-sending subcommands in project/main.py (send, send-batch, supplement, find-one, find-sheet), imported DEFAULT_SEND_TIMEOUT from send_sms.py as the argument's default, and wired args.timeout through as the timeout= keyword to each corresponding send_sms.py function call. The duplicates subcommand and all other existing arguments/defaults were left untouched. Updated project/README.md to move the resolved 'CLI commands do not expose a --timeout option' limitation into 'Current capabilities (v0.1)', rephrased to describe the new capability, while leaving the other three limitations bullets unchanged. No Bash/test-execution tool is available under this agent's 'edit' permission profile, so Point 2's verification was done by reading the diff (per that point's own acceptance criteria, which explicitly calls for a read-time check, not a new automated test) — consistent with the Intent's explicit statement that no new test coverage for main.py is added by this contract.

---

# Implementation Review

_Awaiting implementation review._

---

# Lessons Learned

_Not filled in._

---

<!-- CONTRACT-META
{
  "number": 4,
  "title": "Add --timeout CLI parity to main.py's SMS-sending subcommands",
  "status": "READY_FOR_REVIEWER",
  "created_by": "architect",
  "assigned_to": "reviewer",
  "handoff_to": "reviewer",
  "created_at": "2026-08-18T15:29:30+02:00",
  "updated_at": "2026-08-18T15:32:54+02:00",
  "points": [
    {
      "number": 1,
      "assignment": "Import DEFAULT_SEND_TIMEOUT from send_sms in project/main.py, and add a --timeout float argument (default DEFAULT_SEND_TIMEOUT) to each of the five subparsers that send something over HTTP: send, send-batch, supplement, find-one, find-sheet.",
      "acceptance_criteria": [
        "project/main.py's import from send_sms includes DEFAULT_SEND_TIMEOUT alongside the existing imported names",
        "send_parser, batch_parser (send-batch), supplement_parser, find_one_parser, and find_sheet_parser each gain a `--timeout` argument with `type=float` and `default=DEFAULT_SEND_TIMEOUT`, with a help string describing it as the HTTP timeout for the gateway request in seconds",
        "duplicates_parser does not gain a --timeout argument",
        "No existing argument on any of the six subparsers (--phone, --message, --gate, --batch-size, --pause-seconds, --dry-run, --continue-on-error, --number, --config, --verbose) is removed, renamed, or has its default changed"
      ],
      "programmer_note": "Imported DEFAULT_SEND_TIMEOUT into project/main.py's existing `from send_sms import (...)` block (alongside ConfigurationError, SpreadsheetError, and the five functions). Added a `--timeout` argument (type=float, default=DEFAULT_SEND_TIMEOUT, help='HTTP timeout for the gateway request, in seconds.') to send_parser, batch_parser (send-batch), supplement_parser, find_one_parser, and find_sheet_parser. duplicates_parser was left unchanged with only --gate. No existing argument (--phone, --message, --gate, --batch-size, --pause-seconds, --dry-run, --continue-on-error, --number, --config, --verbose) was removed, renamed, or had its default altered.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T15:32:54+02:00",
      "programmer_files": [
        "project/main.py"
      ],
      "programmer_tests": [
        "Manual read-through of project/main.py after edits: confirmed all five target subparsers gained --timeout (type=float, default=DEFAULT_SEND_TIMEOUT), duplicates_parser did not, and all five corresponding main() call sites pass timeout=args.timeout while the duplicates call site is unchanged.",
        "Manual read-through of project/send_sms.py: confirmed timeout is keyword-only with default DEFAULT_SEND_TIMEOUT (=10.0) on poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, and najit_cisla_ze_seznamu_na_zavore, and that najit_duplikaty has no timeout parameter.",
        "Manual read-through of project/README.md after edits: confirmed the --timeout bullet moved from 'Current limitations' into 'Current capabilities (v0.1)' and the other three limitations bullets are untouched."
      ],
      "reviewer_note": "",
      "reviewer_note_author": "",
      "reviewer_note_at": "",
      "status": "IMPLEMENTED"
    },
    {
      "number": 2,
      "assignment": "In main()'s command dispatch, pass the parsed timeout value through to the corresponding send_sms.py function call for each of the five subcommands touched by the previous point.",
      "acceptance_criteria": [
        "The 'send' branch calls poslat_sms(..., timeout=args.timeout, ...)",
        "The 'send-batch' branch calls poslat_davkove_sms(..., timeout=args.timeout, ...)",
        "The 'supplement' branch calls doplneni_seznamu_zavor(..., timeout=args.timeout, ...)",
        "The 'find-one' branch calls najit_cislo_na_zavore(..., timeout=args.timeout, ...)",
        "The 'find-sheet' branch calls najit_cisla_ze_seznamu_na_zavore(..., timeout=args.timeout, ...)",
        "The 'duplicates' branch (najit_duplikaty call) is unchanged and receives no timeout argument",
        "Running main.py with no --timeout flag on any of the five subcommands produces the exact same effective timeout value as before this change (DEFAULT_SEND_TIMEOUT), verified by reading that the new default matches the value each function already fell back to"
      ],
      "programmer_note": "Updated main()'s five dispatch branches to pass timeout=args.timeout: poslat_sms (send), poslat_davkove_sms (send-batch), doplneni_seznamu_zavor (supplement), najit_cislo_na_zavore (find-one), and najit_cisla_ze_seznamu_na_zavore (find-sheet). The duplicates branch's najit_duplikaty(args.gate, config_path=args.config) call was left unchanged (that function has no timeout parameter). Verified by reading send_sms.py that timeout is a keyword-only parameter (after `*`) on all five target functions, each defaulting to DEFAULT_SEND_TIMEOUT (10.0), so the new CLI --timeout default is byte-for-byte identical to what each function already fell back to when the flag is omitted — no behavior change for existing callers. No automated test was run/added (none was in scope for this point; the contract's Intent explicitly excludes it and Point 2's own acceptance criterion is phrased as a read-time check).",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T15:32:54+02:00",
      "programmer_files": [
        "project/main.py"
      ],
      "programmer_tests": [
        "Manual read-through of project/main.py after edits: confirmed all five target subparsers gained --timeout (type=float, default=DEFAULT_SEND_TIMEOUT), duplicates_parser did not, and all five corresponding main() call sites pass timeout=args.timeout while the duplicates call site is unchanged.",
        "Manual read-through of project/send_sms.py: confirmed timeout is keyword-only with default DEFAULT_SEND_TIMEOUT (=10.0) on poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, and najit_cisla_ze_seznamu_na_zavore, and that najit_duplikaty has no timeout parameter.",
        "Manual read-through of project/README.md after edits: confirmed the --timeout bullet moved from 'Current limitations' into 'Current capabilities (v0.1)' and the other three limitations bullets are untouched."
      ],
      "reviewer_note": "",
      "reviewer_note_author": "",
      "reviewer_note_at": "",
      "status": "IMPLEMENTED"
    },
    {
      "number": 3,
      "assignment": "Update project/README.md to move the now-resolved 'CLI commands do not expose a --timeout option, unlike the Streamlit UI' bullet out of 'Current limitations' and into 'Current capabilities (v0.1)', rephrased to state the capability now exists.",
      "acceptance_criteria": [
        "The 'Current limitations' section no longer contains the 'CLI commands do not expose a --timeout option' bullet (or equivalent wording)",
        "The 'Current capabilities (v0.1)' section contains a new bullet or clause stating that the CLI's SMS-sending subcommands now accept a --timeout option, matching the Streamlit UI",
        "The other three 'Current limitations' bullets (missing tests for main.py/streamlit_app.py, stale-lock recovery, single global phone-column-index assumption) remain present and unaltered",
        "No other section of project/README.md is modified"
      ],
      "programmer_note": "Removed the 'CLI commands do not expose a `--timeout` option, unlike the Streamlit UI.' bullet from README.md's 'Current limitations' section. Added a sentence to the existing `main.py` bullet in 'Current capabilities (v0.1)' stating the five SMS-sending subcommands now accept a --timeout option matching the Streamlit UI. The other three 'Current limitations' bullets (missing main.py/streamlit_app.py tests, stale-lock recovery, single global phone-column-index assumption) were left present and unaltered, and no other section of README.md was touched.",
      "programmer_note_author": "programmer",
      "programmer_note_at": "2026-08-18T15:32:54+02:00",
      "programmer_files": [
        "project/README.md"
      ],
      "programmer_tests": [
        "Manual read-through of project/main.py after edits: confirmed all five target subparsers gained --timeout (type=float, default=DEFAULT_SEND_TIMEOUT), duplicates_parser did not, and all five corresponding main() call sites pass timeout=args.timeout while the duplicates call site is unchanged.",
        "Manual read-through of project/send_sms.py: confirmed timeout is keyword-only with default DEFAULT_SEND_TIMEOUT (=10.0) on poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, and najit_cisla_ze_seznamu_na_zavore, and that najit_duplikaty has no timeout parameter.",
        "Manual read-through of project/README.md after edits: confirmed the --timeout bullet moved from 'Current limitations' into 'Current capabilities (v0.1)' and the other three limitations bullets are untouched."
      ],
      "reviewer_note": "",
      "reviewer_note_author": "",
      "reviewer_note_at": "",
      "status": "IMPLEMENTED"
    }
  ],
  "implementer": "programmer",
  "reviewer": "reviewer",
  "risk_level": "standard",
  "purpose": "project/main.py has no way to configure the HTTP timeout used when talking to the SMS gateway — every SMS-sending subcommand silently falls back to send_sms.py's function-level default (DEFAULT_SEND_TIMEOUT, 10.0s), even though every one of those functions already accepts a timeout keyword argument. The Streamlit UI already exposes this per operation (a 'HTTP timeout [s]' number input in each form), so the CLI is inconsistent with it — someone operating the CLI over a slow or flaky gateway connection today has no way to raise the timeout without editing source. This closes that documented parity gap directly, at the smallest possible scope: one new optional flag, wired to a parameter that already exists.",
  "intent": "This is a purely additive change: one new --timeout argument on each of the five subcommands that actually send something over HTTP (send, send-batch, supplement, find-one, find-sheet), wired straight through to the existing timeout keyword each corresponding send_sms.py function already accepts. No function signature, default value, or behavior changes when the flag is omitted — the new argument's own default is send_sms.DEFAULT_SEND_TIMEOUT, exactly what every call already falls back to today, so omitting --timeout is fully backward-compatible. The duplicates subcommand is deliberately left untouched since it never sends anything over HTTP. This does not add any new automated test coverage for main.py itself — CLI argument-parsing tests for main.py are a separate, already-queued follow-up contract (project/README.md's 'no automated tests for main.py' limitation) and adding partial test infrastructure here would blur that boundary. It also updates project/README.md so the limitation it documents does not go stale the moment this lands, consistent with how every prior contract in this series has kept that file's 'Current limitations'/'Current capabilities' split accurate.",
  "current_state": "project/main.py's build_parser() defines six subcommands via argparse: send (--phone, --message), send-batch (--gate, --batch-size, --pause-seconds, --dry-run, --continue-on-error), supplement (same shape as send-batch), find-one (--gate, --number, --dry-run), find-sheet (--gate, --pause-seconds, --dry-run, --continue-on-error), and duplicates (--gate only, lists duplicates without sending anything). None of the six subcommands currently defines a --timeout argument, and main() never passes a timeout= keyword to any of the send_sms.py functions it calls (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore) — each of those functions already has its own `timeout: float = DEFAULT_SEND_TIMEOUT` keyword parameter (DEFAULT_SEND_TIMEOUT = 10.0, defined in send_sms.py) that main.py simply never overrides. main.py's current import block pulls ConfigurationError, SpreadsheetError, doplneni_seznamu_zavor, najit_cisla_ze_seznamu_na_zavore, najit_cislo_na_zavore, najit_duplikaty, poslat_davkove_sms, poslat_sms from send_sms — DEFAULT_SEND_TIMEOUT is not currently imported into main.py. project/README.md's 'Current limitations' section (most recently updated by IMPLEMENTATION_CONTRACT_0003) currently contains the bullet 'CLI commands do not expose a `--timeout` option, unlike the Streamlit UI.' among four listed limitations.",
  "inputs": "The existing project/main.py build_parser() and main() functions; the existing timeout keyword parameters already present on poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, and najit_cisla_ze_seznamu_na_zavore in project/send_sms.py; DEFAULT_SEND_TIMEOUT's existing value in project/send_sms.py; project/README.md's current 'Current limitations' and 'Current capabilities (v0.1)' sections.",
  "outputs": "Modified project/main.py: a new --timeout float argument on the send, send-batch, supplement, find-one, and find-sheet subparsers (default send_sms.DEFAULT_SEND_TIMEOUT), and the parsed value passed as timeout=args.timeout to each corresponding send_sms.py function call in main(). Modified project/README.md: the 'CLI commands do not expose a --timeout option' bullet moved out of 'Current limitations' into 'Current capabilities (v0.1)'. No other file is created or modified.",
  "out_of_scope": "This contract SHALL NOT add a --timeout argument to the duplicates subcommand — it sends nothing over HTTP, so timeout does not apply to it. It SHALL NOT add any new automated test coverage for project/main.py (CLI argument-parsing/exit-code tests for main.py remain a separate, already-queued follow-up item). It SHALL NOT modify project/send_sms.py or project/streamlit_app.py — the timeout keyword parameters and DEFAULT_SEND_TIMEOUT this contract wires into already exist and are unchanged. It SHALL NOT change DEFAULT_SEND_TIMEOUT's value or any other subcommand's existing arguments/behavior. It SHALL NOT modify any section of project/README.md other than moving the one named bullet between 'Current limitations' and 'Current capabilities (v0.1)'.",
  "future_evolution": "CLI argument-parsing test coverage for project/main.py (which would include a test asserting --timeout is parsed and defaulted correctly) is deferred to the already-queued, separate 'missing tests for main.py/streamlit_app.py' follow-up contract. The remaining limitations documented in project/README.md (per-gate phone-column configuration, stale-lock recovery) stay deferred to their own future contracts, untouched by this change.",
  "lessons_learned": "",
  "architecture_review_rounds": [
    {
      "round": 1,
      "date": "2026-08-18T15:30:58+02:00",
      "verdict": "ACCEPTED",
      "reviewer": "reviewer",
      "findings": "Verified the contract's factual claims directly against project/main.py, project/send_sms.py, and project/README.md (per PRINCIPLES.md P7/P6 — Current State must be established from the actual code, not memory). Result: every claim in 'Current State' is accurate. build_parser() defines exactly the six subcommands and argument sets described, none currently has --timeout, and main() never passes timeout= to any send_sms.py call. All five target functions (poslat_sms, poslat_davkove_sms, doplneni_seznamu_zavor, najit_cislo_na_zavore, najit_cisla_ze_seznamu_na_zavore) have a keyword-only `timeout: float = DEFAULT_SEND_TIMEOUT` parameter (DEFAULT_SEND_TIMEOUT = 10.0, defined at send_sms.py:26); najit_duplikaty has no timeout parameter, confirming duplicates is correctly excluded. main.py's current import statement indeed omits DEFAULT_SEND_TIMEOUT. project/README.md's 'Current limitations' section contains the exact bullet quoted in the contract ('CLI commands do not expose a `--timeout` option, unlike the Streamlit UI.'), and the other three limitations bullets named in Point 3's acceptance criteria (missing tests for main.py/streamlit_app.py, stale-lock recovery, single global phone-column-index assumption) are present and match.\n\nPurpose/Intent check: this closes a real, already-documented gap (the README's own limitations bullet, added by CONTRACT_0003) rather than anticipating a future need — consistent with P1/P8. It is deliberately minimal (one flag, wired to an already-existing parameter), not a premature abstraction.\n\nPoints are actionable in stated order and each acceptance criterion is concretely verifiable by reading the diff (parser definitions, call-site keyword, README section membership) — none require guessing. Because every target function takes `timeout` as keyword-only (after `*`), `timeout=args.timeout` is unambiguous regardless of call-site argument order, so no implementation choice is left open. Point 2's 'produces the exact same effective timeout value... verified by reading' is explicitly a read-time check, not a new test, which matches the Intent's explicit statement that no automated test coverage is added here (deferred to the already-queued main.py test contract) — internally consistent, no contradiction.\n\nOut of Scope explicitly addresses the main edge case (duplicates subcommand, which has no timeout parameter at all) and forecloses scope creep into send_sms.py, streamlit_app.py, DEFAULT_SEND_TIMEOUT's value, other subcommand args, and unrelated README sections — no ambiguity for the programmer to resolve.\n\nBackward compatibility: explicitly preserved — new argument's own default equals the value every call already silently used, verified against the actual DEFAULT_SEND_TIMEOUT constant and each function's existing default; no signature or default changes to existing arguments. No violation.\n\nScope/permissions: only project/main.py and project/README.md are touched, both already inside project/ (AGENTS.md/ADR-022's default write scope — no framework or governance file touched, so no separate scope point was needed). No shell/git command is required by any point (per the CONTRACT_0002 architecture-review finding on record, the programmer's 'edit' permission profile has no Bash) — Point 2's verification step is explicitly satisfied by reading, not by running anything, so this contract is fully executable under the programmer's actual tool access.\n\nNaming convention: no new file/directory is proposed, so ADR-008's convention does not apply here.\n\nRisk level: checked against Tr5-base decision 7's criteria (real credentials/API keys, real calls to external systems, native/hardware libraries, risk of landing personal/real data in git). This contract adds no new external call, credential, or data-handling path — it only threads an existing timeout value through argparse to an existing keyword argument. 'standard' is the correct classification; no escalation warranted."
    }
  ],
  "completion_notes": "Added --timeout float CLI argument to the five SMS-sending subcommands in project/main.py (send, send-batch, supplement, find-one, find-sheet), imported DEFAULT_SEND_TIMEOUT from send_sms.py as the argument's default, and wired args.timeout through as the timeout= keyword to each corresponding send_sms.py function call. The duplicates subcommand and all other existing arguments/defaults were left untouched. Updated project/README.md to move the resolved 'CLI commands do not expose a --timeout option' limitation into 'Current capabilities (v0.1)', rephrased to describe the new capability, while leaving the other three limitations bullets unchanged. No Bash/test-execution tool is available under this agent's 'edit' permission profile, so Point 2's verification was done by reading the diff (per that point's own acceptance criteria, which explicitly calls for a read-time check, not a new automated test) — consistent with the Intent's explicit statement that no new test coverage for main.py is added by this contract.",
  "implementation_review_rounds": []
}
CONTRACT-META -->
