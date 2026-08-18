# IMPLEMENTATION_CONTRACT_0002

Status: READY_FOR_PROGRAMMER

---

# Workflow

- Created by: `architect`
- Reviewer (both review gates): `reviewer`
- Implementer: `programmer`
- Risk level: `standard`
- Currently with: `programmer`
- Handed off to: `programmer`
- Created at: `2026-08-18T11:46:11+02:00`
- Updated at: `2026-08-18T12:44:25+02:00`

---

# Title

Migrate SMS gateway application from read-only source/project/ into project/

---

# Purpose

The real SMS gateway application (CLI, Streamlit UI, core logic, tests) currently exists only inside source/project/, which AGENTS.md and ADR-024 define as a read-only migration reference that must never be edited directly. project/, the directory the architecture designates for actual application code built through the contract pipeline (ADR-016), is still an empty placeholder. This blocks all further work: the pending README correction (IMPLEMENTATION_CONTRACT_0001) and every planned follow-up fix (Excel concurrent-write locking, CLI/UI parameter parity, per-gate column configuration, additional test coverage) target code that legally cannot be touched where it currently sits. This migration moves the application to its correct, editable home so that work can continue.

---

# Intent

This change is a faithful, behavior-preserving copy of the existing application files from source/project/ into project/, plus one .gitignore safeguard for the config file that will eventually live there. It deliberately does not change any code, fix any of the previously identified limitations, or touch project/README.md's content — those are separate, already-identified follow-up contracts (the README correction specifically resumes as a revision of IMPLEMENTATION_CONTRACT_0001 once this lands). source/project/ is read only during and after this change; nothing under source/ is modified, added, or removed. Every point is deliberately scoped to what the programmer's actual tool access (Read, Grep, Glob, Edit, Write — no Bash) can perform and verify; setting up a runnable environment and executing the test suite requires shell access the programmer does not have, so that verification step is explicitly handed to the owner as a manual follow-up rather than attempted inside the contract.

---

# Current State

project/ contains only project/README.md (the generic Tr5-base placeholder). source/project/ contains the full working application: send_sms.py (core logic), main.py (CLI with subcommands send, send-batch, supplement, find-one, find-sheet, duplicates), streamlit_app.py (Streamlit UI), pyproject.toml, config.example.toml, tests/test_send_sms.py (8 unit tests), SESSION_2026-04-10.md (session log), source/project/README.md (a copy of the same generic Tr5-base placeholder, present but not touched by this contract), and source/project/.gitignore (ignoring .idea/, .venv/, __pycache__/, *.pyc, config.toml — local to source/project/ only). The repository root .gitignore (.env, __pycache__/, .venv/, .pytest_cache/, .pytest-tmp/, .idea/, agents/*/runtime/*, agents/*/logs/, .discovery/) does not currently ignore any config.toml pattern, but already has an unanchored `.venv/` pattern that will cover a future project/.venv whenever the owner creates one manually. No config.toml (real or otherwise) exists anywhere in the repository today. The repository root requirements.txt lists only the framework's own dependencies (openai-codex, claude-agent-sdk, python-dotenv, pytest, pyaudio, google-genai) — none of the application's runtime dependencies (openpyxl, pandas, requests, streamlit, declared in source/project/pyproject.toml) are installed anywhere reachable by a fresh checkout. The programmer's Claude permission_profile is 'edit', which grants only Read, Grep, Glob, Edit, and Write tools (confirmed in agents/agent.py's CLAUDE_EDIT_TOOLS and agents/programmer/config.json) — no Bash tool is available, so no git, pip, venv, or test-runner command can be executed as part of this contract's implementation.

---

# Inputs

The existing files under source/project/: send_sms.py, main.py, streamlit_app.py, pyproject.toml, config.example.toml, tests/test_send_sms.py, SESSION_2026-04-10.md — used as the verbatim source content for the copy. The existing root-level .gitignore content, to which one line is added.

---

# Outputs

New files: project/send_sms.py, project/main.py, project/streamlit_app.py, project/pyproject.toml, project/config.example.toml, project/tests/test_send_sms.py, and project/SESSION_2026_04_10.md (renamed from the source's hyphenated SESSION_2026-04-10.md per ADR-008's no-hyphens naming convention; content otherwise byte-for-byte identical). One modified file: the repository root .gitignore, with a new 'config.toml' entry. source/project/ and every other path under source/ remain byte-for-byte unchanged. project/README.md remains unchanged (out of scope here). No virtual environment, installed dependency, or test-execution result is produced by this contract.

---

# Functional Requirements

## Point 1

SHALL: Copy source/project/send_sms.py verbatim to project/send_sms.py.

Acceptance criteria:
- project/send_sms.py exists and its content is byte-for-byte identical to source/project/send_sms.py at the time of copying
- source/project/send_sms.py is unchanged after the operation

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 2

SHALL: Copy source/project/main.py verbatim to project/main.py.

Acceptance criteria:
- project/main.py exists and its content is byte-for-byte identical to source/project/main.py at the time of copying
- source/project/main.py is unchanged after the operation

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 3

SHALL: Copy source/project/streamlit_app.py verbatim to project/streamlit_app.py.

Acceptance criteria:
- project/streamlit_app.py exists and its content is byte-for-byte identical to source/project/streamlit_app.py at the time of copying
- source/project/streamlit_app.py is unchanged after the operation

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 4

SHALL: Copy source/project/pyproject.toml verbatim to project/pyproject.toml.

Acceptance criteria:
- project/pyproject.toml exists and its content is byte-for-byte identical to source/project/pyproject.toml at the time of copying
- source/project/pyproject.toml is unchanged after the operation

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 5

SHALL: Copy source/project/config.example.toml verbatim to project/config.example.toml.

Acceptance criteria:
- project/config.example.toml exists and its content is byte-for-byte identical to source/project/config.example.toml at the time of copying
- source/project/config.example.toml is unchanged after the operation
- No project/config.toml (a real, non-example config file) is created as part of this point

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 6

SHALL: Create the project/tests/ directory and copy source/project/tests/test_send_sms.py verbatim to project/tests/test_send_sms.py.

Acceptance criteria:
- project/tests/test_send_sms.py exists and its content is byte-for-byte identical to source/project/tests/test_send_sms.py at the time of copying
- source/project/tests/test_send_sms.py is unchanged after the operation

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 7

SHALL: Copy the content of source/project/SESSION_2026-04-10.md verbatim to a new file named project/SESSION_2026_04_10.md (underscores instead of hyphens in the date, per ADR-008's no-hyphens naming convention, which applies to new files under the governed project/ tree).

Acceptance criteria:
- project/SESSION_2026_04_10.md exists and its content is byte-for-byte identical to source/project/SESSION_2026-04-10.md at the time of copying
- No file named project/SESSION_2026-04-10.md (with hyphens) is created
- source/project/SESSION_2026-04-10.md is unchanged after the operation

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 8

SHALL: Add a 'config.toml' entry to the repository root-level .gitignore so that any future project/config.toml (holding real gateway credentials) is never committed.

Acceptance criteria:
- Reading the updated root .gitignore shows a line that is exactly 'config.toml' (unanchored, so it also matches project/config.toml)
- Reading the updated root .gitignore shows every line that existed before this edit is still present and unaltered, with only the new 'config.toml' line added
- No project/.gitignore file is created as part of this point

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

## Point 9

SHALL: Verify that source/ remains completely untouched by this migration, using a file listing rather than any version-control command.

Acceptance criteria:
- A Glob listing of source/project/ performed after all copy operations enumerates exactly the same files as before this contract began: send_sms.py, main.py, streamlit_app.py, pyproject.toml, config.example.toml, tests/test_send_sms.py, SESSION_2026-04-10.md, README.md, and .gitignore — no file added, removed, or renamed
- For each of the seven files copied in points 1-7, its own point's 'unchanged after the operation' criterion is confirmed to still hold at this final check
- A Glob listing of source/ outside source/project/ shows no new, removed, or renamed file compared to before this contract began

> Status: PENDING

Programmer note:

_Awaiting implementation._

Reviewer's implementation review for this point:

_Awaiting review._

---

# Out of Scope

This contract SHALL NOT modify, add to, or remove anything under source/ (it stays exactly as a read-only reference). It SHALL NOT change the content of project/README.md — that is handled separately by revising IMPLEMENTATION_CONTRACT_0001 after this migration lands. It SHALL NOT alter the behavior, logic, or structure of any copied file — this is a verbatim copy, not a rewrite. It SHALL NOT create a project/.gitignore file or copy source/project/.gitignore — only the root-level .gitignore is modified, and only with the single 'config.toml' entry requested. It SHALL NOT address any previously identified limitation (Excel concurrent-write locking, CLI/UI --timeout parity, per-gate phone-column configuration, additional test coverage for main.py/streamlit_app.py) — those remain deferred to their own future contracts. It SHALL NOT create project/.venv, install project dependencies (openpyxl, pandas, requests, streamlit), or execute the test suite — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash access needed for `python -m venv`, `pip install`, or running `python -m unittest`/pytest. Setting up that environment and confirming the migrated test suite (project/tests/test_send_sms.py, 8 tests) actually passes in its new location is a manual step for the owner to perform after this contract is committed — it is not part of this contract's automated points.

---

# Acceptance Criteria

Acceptance criteria are listed per point in the Functional Requirements section.

---

# Architecture Review

### Round 1 — 2026-08-18T11:49:40+02:00 — Verdict: CHANGES_REQUESTED — Reviewer: `reviewer`

Checked against AGENTS.md (project/ vs source/ scoping rule, ADR-024's 'read-only, never edited directly', ADR-022's write-scope rule, ADR-008 naming convention), memory/DECISIONS.md (ADR-016, ADR-022, ADR-024, decision 7's risk criteria, and the prior IMPLEMENTATION_CONTRACT_0001 round-1 review which explicitly recommended exactly this kind of migration contract as the correct fix), and the actual repository contents (source/project/*, memory/CURRENT_STATE.md's Discovery Engine scan, root .gitignore, root requirements.txt).

What holds up: Purpose/Intent describe a real, already-identified architectural need (not a premature abstraction) — this contract is precisely what the reviewer recommended in IMPLEMENTATION_CONTRACT_0001's round 1 ('scope this as part of an actual migration contract that moves the code from source/project/ into project/ per ADR-024's intended flow'). Current State's file inventory for source/project/ was verified directly against the filesystem and against memory/CURRENT_STATE.md's Discovery Engine output and matches (send_sms.py, main.py, streamlit_app.py, pyproject.toml, config.example.toml, tests/test_send_sms.py, SESSION_2026-04-10.md, source/project/.gitignore content all confirmed byte-accurate). Out of Scope is explicit about source/ staying untouched, project/README.md staying untouched, and no project/.gitignore being created. Point 8's gitignore acceptance criteria correctly implement PRINCIPLES.md P5 (gitignore coverage as an acceptance criterion of the change introducing the sensitive path). No destructive commands, no access beyond the programmer's `edit` profile, no backward-compatibility break (project/ was an empty placeholder). risk_level `standard` was independently verified as correct, not merely accepted: config.example.toml contains only placeholder values (example gateway URL, example UNC path, dummy phone/password), send_sms.py has no hardcoded real credentials (password is always loaded from config.toml at runtime, which is gitignored), and point 9's test suite uses a FakeClient (no real network calls) — no real credentials, no real external calls, no native/hardware libraries, no personal/real data risk. No escalation warranted.

Two real, fixable gaps found by direct verification (not assumption):
1. Naming convention violation (ADR-008/AGENTS.md, 'No hyphens in file or directory names — use _ instead of -'): Point 7 creates project/SESSION_2026-04-10.md, a genuinely new file under the governed project/ tree (not the preserved-as-is source/ reference), whose name contains hyphens. The contract's 'Intent' frames this as a purely verbatim, name-preserving copy and never addresses this conflict — the programmer is left to silently violate an explicit repo-wide naming rule or silently rename a file the contract calls 'byte-for-byte identical', neither of which the contract authorizes.
2. Point 9's acceptance criteria (8 tests passing) are not achievable as written without a Python environment that has openpyxl, pandas, and requests installed (confirmed via source/project/pyproject.toml's dependency list and by reading send_sms.py's and test_send_sms.py's actual imports) — none of which are in the repository's root requirements.txt (the framework's own shared environment). Current State, Inputs, and the points say nothing about how this environment is obtained (installing into the shared framework venv, using source/project/.venv, or creating a new project-scoped venv are all live options the contract leaves for the programmer to invent). Per PRINCIPLES.md P13, a real gap requiring an environment/dependency decision should be resolved by the contract, not improvised by the programmer.

Minor, non-blocking note: Current State omits that source/project/README.md exists (confirmed present via filesystem and memory/CURRENT_STATE.md); it does not cause ambiguity here since the Outputs list is an exhaustive, closed set and Out of Scope already excludes project/README.md content, but it is a small P6 completeness gap worth the architect tightening while revising the other two points.

### Round 2 — 2026-08-18T12:05:27+02:00 — Verdict: CHANGES_REQUESTED — Reviewer: `reviewer`

Checked the current contract text against AGENTS.md (project/ vs source/ scoping, ADR-024 read-only rule, ADR-008 naming convention, root .gitignore fixed-file-set rule), memory/DECISIONS.md (ADR-016, ADR-022, ADR-024, ADR-028/ADR-029's decision-1/decision-9 reviewer model, decision 7's risk criteria), the actual repository contents (source/project/* file inventory, source/project/pyproject.toml's dependency list, send_sms.py's and tests/test_send_sms.py's actual imports, config.example.toml's placeholder-only content, root .gitignore, root requirements.txt), and — new in this round — the actual programmer/reviewer/architect permission mechanics in agents/agent.py and each agent's config.json.

First, verified that this round's two structural gaps are now genuinely resolved in the current point text, not just claimed: Point 7 now explicitly states the ADR-008 hyphen-to-underscore rationale for renaming SESSION_2026-04-10.md to SESSION_2026_04_10.md and adds an explicit criterion that no hyphenated file is created — resolves the earlier naming-convention gap. Points 9-11 now explicitly own the dependency-environment question (project-scoped project/.venv, install of openpyxl/pandas/requests/streamlit, matching project/pyproject.toml's actual declared constraints which I independently re-verified against the file and against send_sms.py's/test_send_sms.py's real import statements) instead of leaving it for the programmer to invent — resolves the earlier P13 gap in principle.

However, direct verification of the tool-permission mechanics surfaces a new, concrete, blocking problem that was not present in round 1's findings: agents/programmer/config.json sets permission_profile 'edit' and provider 'claude'; agents/agent.py's _claude_permissions() maps 'edit' to CLAUDE_EDIT_TOOLS = (Read, Grep, Glob, Edit, Write) — no Bash tool at all (Bash is only granted under CLAUDE_FULL_TOOLS, i.e. permission_profile 'full', which no agent in this pipeline uses; architect and reviewer both use 'review', which is Read/Grep/Glob only, even more restricted). This means the programmer has no mechanism to execute a shell command of any kind. Yet: Point 8's acceptance criteria requires running `git check-ignore project/config.toml`; Point 9 requires `python -m venv`, then `pip show` to verify installed versions; Point 10 requires invoking `project/.venv/Scripts/python -m unittest discover ...`; Point 11 requires `git status`/`git diff`. None of these are achievable through Read/Grep/Glob/Edit/Write. Points 1-7 (verbatim file copies via Read+Write) are fine and require no shell access. This is exactly the check the reviewer is asked to make ('does the contract require destructive commands or access beyond the programmer profile (edit)?') — the answer for points 8-11 as currently worded is yes, and it is a real capability gap, not a hypothesis: confirmed by reading agents/agent.py's tool-mapping code and every agent's config.json directly.

This is fixable by rewriting, not an architecturally wrong request as a whole (the migration itself, and the underlying need for a project-scoped venv and gitignore entry, both remain sound and necessary) — hence CHANGES_REQUESTED, not REJECTED. The architect needs to either (a) rework points 8-11's acceptance criteria so verification does not depend on Bash-tool command execution the programmer cannot perform (e.g. state the intended git/pip/venv commands as instructions for the human owner to run and confirm outside the automated contract points, mirroring how every existing ADR's own 'Verification: python -m pytest -q — N/N passing' line in memory/DECISIONS.md was clearly performed by a human, not an agent tool call), or (b) explicitly scope points 9-10 out of this contract and hand dependency installation/test execution to the owner as a documented manual follow-up, keeping only the achievable Write-tool actions (the .gitignore edit itself in point 8, minus its git check-ignore verification step) inside the programmer's actual points.

Risk_level: independently re-verified as correctly 'standard' — config.example.toml (re-read directly) contains only placeholder values (example gateway host, example UNC path, dummy phone numbers/passwords '1234'), no real credentials are copied or introduced, and the FakeClient-based test suite makes no real network calls. A pip install against the public PyPI registry (needed if point 9 survives revision) is routine dependency tooling, not the kind of 'real call to an external system' decision 7's criteria target (business/API integration, not package installation) — no escalation warranted on that basis alone.

### Round 3 — 2026-08-18T12:44:25+02:00 — Verdict: ACCEPTED — Reviewer: `reviewer`

Independently re-verified this contract (round 3, fresh thread per Tr5-base decision 9) against AGENTS.md, memory/DECISIONS.md (ADR-008, ADR-016, ADR-022, ADR-024, ADR-029, decision 7's risk criteria), and the live repository state — not against the prior two rounds' text alone. Both blocking gaps from rounds 1 and 2 are genuinely resolved in the current point text: (1) Point 7 now renames SESSION_2026-04-10.md to SESSION_2026_04_10.md with the ADR-008 rationale stated and an explicit no-hyphenated-file criterion; independently confirmed all 7 other output filenames (send_sms.py, main.py, streamlit_app.py, pyproject.toml, config.example.toml, tests/test_send_sms.py) are already lowercase_with_underscores, no hyphens/diacritics. (2) Re-read agents/agent.py directly: CLAUDE_EDIT_TOOLS = (Read, Grep, Glob, Edit, Write), no Bash, matching agents/programmer/config.json's permission_profile 'edit'. Point 8's acceptance criteria now read the updated .gitignore via Read rather than `git check-ignore`, and Point 9 verifies via Glob listing rather than `git status`/`git diff` — all 9 points are achievable with Read/Grep/Glob/Edit/Write alone, no Bash-dependent step remains. Out of Scope now explicitly excludes venv creation, dependency install, and test execution as a documented manual owner follow-up, closing the earlier P13 environment-decision gap rather than leaving it for the programmer to invent. Fresh-filesystem verification of Current State's claims: project/ contains only the placeholder README.md; source/project/ contains exactly the 9 items Point 9 enumerates (verified via Glob); project/tests/ does not yet exist (Point 6 correctly creates it); root .gitignore has no config.toml entry and already has an unanchored .venv/ pattern; root requirements.txt lacks openpyxl/pandas/requests/streamlit, which are confirmed real imports in send_sms.py/main.py/streamlit_app.py and declared in source/project/pyproject.toml. risk_level 'standard' independently re-verified against decision 7's criteria: config.example.toml (read directly) contains placeholder-only values, SESSION_2026-04-10.md (read directly) contains no personal/real data, and tests/test_send_sms.py (read directly) uses a FakeClient with no real network calls — no escalation warranted. Out of Scope is explicit and complete: source/ untouched, project/README.md untouched (deferred to Contract 0001's revision), no project/.gitignore, no behavior changes. Point 8's root-.gitignore edit is correctly scoped as its own explicit point per ADR-022's 'a change outside project/ needs its own contract point' rule. No backward-compatibility issue (project/ was an empty placeholder). Both prior review-round lessons are already recorded in memory/DECISIONS.md (2026-08-18T11:49:50+02:00 and 2026-08-18T12:05:37+02:00 entries) — no duplicate entry needed. The contract is complete, actionable, verifiable, and within the programmer's actual tool access; it may proceed to implementation.

---

# Future Evolution

Once this migration lands and the owner has manually confirmed (outside this contract) that the migrated test suite passes from project/, IMPLEMENTATION_CONTRACT_0001 is revised to target project/README.md with content accurately describing the now-migrated application. Subsequent, separate contracts will address the limitations already identified in the architect's code review (no file locking for concurrent Excel writes, missing CLI --timeout options, no tests for main.py/streamlit_app.py, the single global phone-column-index assumption) directly on the code now living in project/.

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
  "number": 2,
  "title": "Migrate SMS gateway application from read-only source/project/ into project/",
  "status": "READY_FOR_PROGRAMMER",
  "created_by": "architect",
  "assigned_to": "programmer",
  "handoff_to": "programmer",
  "created_at": "2026-08-18T11:46:11+02:00",
  "updated_at": "2026-08-18T12:44:25+02:00",
  "points": [
    {
      "number": 1,
      "assignment": "Copy source/project/send_sms.py verbatim to project/send_sms.py.",
      "acceptance_criteria": [
        "project/send_sms.py exists and its content is byte-for-byte identical to source/project/send_sms.py at the time of copying",
        "source/project/send_sms.py is unchanged after the operation"
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
      "assignment": "Copy source/project/main.py verbatim to project/main.py.",
      "acceptance_criteria": [
        "project/main.py exists and its content is byte-for-byte identical to source/project/main.py at the time of copying",
        "source/project/main.py is unchanged after the operation"
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
      "assignment": "Copy source/project/streamlit_app.py verbatim to project/streamlit_app.py.",
      "acceptance_criteria": [
        "project/streamlit_app.py exists and its content is byte-for-byte identical to source/project/streamlit_app.py at the time of copying",
        "source/project/streamlit_app.py is unchanged after the operation"
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
      "assignment": "Copy source/project/pyproject.toml verbatim to project/pyproject.toml.",
      "acceptance_criteria": [
        "project/pyproject.toml exists and its content is byte-for-byte identical to source/project/pyproject.toml at the time of copying",
        "source/project/pyproject.toml is unchanged after the operation"
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
      "assignment": "Copy source/project/config.example.toml verbatim to project/config.example.toml.",
      "acceptance_criteria": [
        "project/config.example.toml exists and its content is byte-for-byte identical to source/project/config.example.toml at the time of copying",
        "source/project/config.example.toml is unchanged after the operation",
        "No project/config.toml (a real, non-example config file) is created as part of this point"
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
      "assignment": "Create the project/tests/ directory and copy source/project/tests/test_send_sms.py verbatim to project/tests/test_send_sms.py.",
      "acceptance_criteria": [
        "project/tests/test_send_sms.py exists and its content is byte-for-byte identical to source/project/tests/test_send_sms.py at the time of copying",
        "source/project/tests/test_send_sms.py is unchanged after the operation"
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
      "assignment": "Copy the content of source/project/SESSION_2026-04-10.md verbatim to a new file named project/SESSION_2026_04_10.md (underscores instead of hyphens in the date, per ADR-008's no-hyphens naming convention, which applies to new files under the governed project/ tree).",
      "acceptance_criteria": [
        "project/SESSION_2026_04_10.md exists and its content is byte-for-byte identical to source/project/SESSION_2026-04-10.md at the time of copying",
        "No file named project/SESSION_2026-04-10.md (with hyphens) is created",
        "source/project/SESSION_2026-04-10.md is unchanged after the operation"
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
      "number": 8,
      "assignment": "Add a 'config.toml' entry to the repository root-level .gitignore so that any future project/config.toml (holding real gateway credentials) is never committed.",
      "acceptance_criteria": [
        "Reading the updated root .gitignore shows a line that is exactly 'config.toml' (unanchored, so it also matches project/config.toml)",
        "Reading the updated root .gitignore shows every line that existed before this edit is still present and unaltered, with only the new 'config.toml' line added",
        "No project/.gitignore file is created as part of this point"
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
      "number": 9,
      "assignment": "Verify that source/ remains completely untouched by this migration, using a file listing rather than any version-control command.",
      "acceptance_criteria": [
        "A Glob listing of source/project/ performed after all copy operations enumerates exactly the same files as before this contract began: send_sms.py, main.py, streamlit_app.py, pyproject.toml, config.example.toml, tests/test_send_sms.py, SESSION_2026-04-10.md, README.md, and .gitignore — no file added, removed, or renamed",
        "For each of the seven files copied in points 1-7, its own point's 'unchanged after the operation' criterion is confirmed to still hold at this final check",
        "A Glob listing of source/ outside source/project/ shows no new, removed, or renamed file compared to before this contract began"
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
  "purpose": "The real SMS gateway application (CLI, Streamlit UI, core logic, tests) currently exists only inside source/project/, which AGENTS.md and ADR-024 define as a read-only migration reference that must never be edited directly. project/, the directory the architecture designates for actual application code built through the contract pipeline (ADR-016), is still an empty placeholder. This blocks all further work: the pending README correction (IMPLEMENTATION_CONTRACT_0001) and every planned follow-up fix (Excel concurrent-write locking, CLI/UI parameter parity, per-gate column configuration, additional test coverage) target code that legally cannot be touched where it currently sits. This migration moves the application to its correct, editable home so that work can continue.",
  "intent": "This change is a faithful, behavior-preserving copy of the existing application files from source/project/ into project/, plus one .gitignore safeguard for the config file that will eventually live there. It deliberately does not change any code, fix any of the previously identified limitations, or touch project/README.md's content — those are separate, already-identified follow-up contracts (the README correction specifically resumes as a revision of IMPLEMENTATION_CONTRACT_0001 once this lands). source/project/ is read only during and after this change; nothing under source/ is modified, added, or removed. Every point is deliberately scoped to what the programmer's actual tool access (Read, Grep, Glob, Edit, Write — no Bash) can perform and verify; setting up a runnable environment and executing the test suite requires shell access the programmer does not have, so that verification step is explicitly handed to the owner as a manual follow-up rather than attempted inside the contract.",
  "current_state": "project/ contains only project/README.md (the generic Tr5-base placeholder). source/project/ contains the full working application: send_sms.py (core logic), main.py (CLI with subcommands send, send-batch, supplement, find-one, find-sheet, duplicates), streamlit_app.py (Streamlit UI), pyproject.toml, config.example.toml, tests/test_send_sms.py (8 unit tests), SESSION_2026-04-10.md (session log), source/project/README.md (a copy of the same generic Tr5-base placeholder, present but not touched by this contract), and source/project/.gitignore (ignoring .idea/, .venv/, __pycache__/, *.pyc, config.toml — local to source/project/ only). The repository root .gitignore (.env, __pycache__/, .venv/, .pytest_cache/, .pytest-tmp/, .idea/, agents/*/runtime/*, agents/*/logs/, .discovery/) does not currently ignore any config.toml pattern, but already has an unanchored `.venv/` pattern that will cover a future project/.venv whenever the owner creates one manually. No config.toml (real or otherwise) exists anywhere in the repository today. The repository root requirements.txt lists only the framework's own dependencies (openai-codex, claude-agent-sdk, python-dotenv, pytest, pyaudio, google-genai) — none of the application's runtime dependencies (openpyxl, pandas, requests, streamlit, declared in source/project/pyproject.toml) are installed anywhere reachable by a fresh checkout. The programmer's Claude permission_profile is 'edit', which grants only Read, Grep, Glob, Edit, and Write tools (confirmed in agents/agent.py's CLAUDE_EDIT_TOOLS and agents/programmer/config.json) — no Bash tool is available, so no git, pip, venv, or test-runner command can be executed as part of this contract's implementation.",
  "inputs": "The existing files under source/project/: send_sms.py, main.py, streamlit_app.py, pyproject.toml, config.example.toml, tests/test_send_sms.py, SESSION_2026-04-10.md — used as the verbatim source content for the copy. The existing root-level .gitignore content, to which one line is added.",
  "outputs": "New files: project/send_sms.py, project/main.py, project/streamlit_app.py, project/pyproject.toml, project/config.example.toml, project/tests/test_send_sms.py, and project/SESSION_2026_04_10.md (renamed from the source's hyphenated SESSION_2026-04-10.md per ADR-008's no-hyphens naming convention; content otherwise byte-for-byte identical). One modified file: the repository root .gitignore, with a new 'config.toml' entry. source/project/ and every other path under source/ remain byte-for-byte unchanged. project/README.md remains unchanged (out of scope here). No virtual environment, installed dependency, or test-execution result is produced by this contract.",
  "out_of_scope": "This contract SHALL NOT modify, add to, or remove anything under source/ (it stays exactly as a read-only reference). It SHALL NOT change the content of project/README.md — that is handled separately by revising IMPLEMENTATION_CONTRACT_0001 after this migration lands. It SHALL NOT alter the behavior, logic, or structure of any copied file — this is a verbatim copy, not a rewrite. It SHALL NOT create a project/.gitignore file or copy source/project/.gitignore — only the root-level .gitignore is modified, and only with the single 'config.toml' entry requested. It SHALL NOT address any previously identified limitation (Excel concurrent-write locking, CLI/UI --timeout parity, per-gate phone-column configuration, additional test coverage for main.py/streamlit_app.py) — those remain deferred to their own future contracts. It SHALL NOT create project/.venv, install project dependencies (openpyxl, pandas, requests, streamlit), or execute the test suite — the programmer's Claude permission_profile ('edit': Read/Grep/Glob/Edit/Write) has no Bash access needed for `python -m venv`, `pip install`, or running `python -m unittest`/pytest. Setting up that environment and confirming the migrated test suite (project/tests/test_send_sms.py, 8 tests) actually passes in its new location is a manual step for the owner to perform after this contract is committed — it is not part of this contract's automated points.",
  "future_evolution": "Once this migration lands and the owner has manually confirmed (outside this contract) that the migrated test suite passes from project/, IMPLEMENTATION_CONTRACT_0001 is revised to target project/README.md with content accurately describing the now-migrated application. Subsequent, separate contracts will address the limitations already identified in the architect's code review (no file locking for concurrent Excel writes, missing CLI --timeout options, no tests for main.py/streamlit_app.py, the single global phone-column-index assumption) directly on the code now living in project/.",
  "lessons_learned": "",
  "architecture_review_rounds": [
    {
      "round": 1,
      "date": "2026-08-18T11:49:40+02:00",
      "verdict": "CHANGES_REQUESTED",
      "reviewer": "reviewer",
      "findings": "Checked against AGENTS.md (project/ vs source/ scoping rule, ADR-024's 'read-only, never edited directly', ADR-022's write-scope rule, ADR-008 naming convention), memory/DECISIONS.md (ADR-016, ADR-022, ADR-024, decision 7's risk criteria, and the prior IMPLEMENTATION_CONTRACT_0001 round-1 review which explicitly recommended exactly this kind of migration contract as the correct fix), and the actual repository contents (source/project/*, memory/CURRENT_STATE.md's Discovery Engine scan, root .gitignore, root requirements.txt).\n\nWhat holds up: Purpose/Intent describe a real, already-identified architectural need (not a premature abstraction) — this contract is precisely what the reviewer recommended in IMPLEMENTATION_CONTRACT_0001's round 1 ('scope this as part of an actual migration contract that moves the code from source/project/ into project/ per ADR-024's intended flow'). Current State's file inventory for source/project/ was verified directly against the filesystem and against memory/CURRENT_STATE.md's Discovery Engine output and matches (send_sms.py, main.py, streamlit_app.py, pyproject.toml, config.example.toml, tests/test_send_sms.py, SESSION_2026-04-10.md, source/project/.gitignore content all confirmed byte-accurate). Out of Scope is explicit about source/ staying untouched, project/README.md staying untouched, and no project/.gitignore being created. Point 8's gitignore acceptance criteria correctly implement PRINCIPLES.md P5 (gitignore coverage as an acceptance criterion of the change introducing the sensitive path). No destructive commands, no access beyond the programmer's `edit` profile, no backward-compatibility break (project/ was an empty placeholder). risk_level `standard` was independently verified as correct, not merely accepted: config.example.toml contains only placeholder values (example gateway URL, example UNC path, dummy phone/password), send_sms.py has no hardcoded real credentials (password is always loaded from config.toml at runtime, which is gitignored), and point 9's test suite uses a FakeClient (no real network calls) — no real credentials, no real external calls, no native/hardware libraries, no personal/real data risk. No escalation warranted.\n\nTwo real, fixable gaps found by direct verification (not assumption):\n1. Naming convention violation (ADR-008/AGENTS.md, 'No hyphens in file or directory names — use _ instead of -'): Point 7 creates project/SESSION_2026-04-10.md, a genuinely new file under the governed project/ tree (not the preserved-as-is source/ reference), whose name contains hyphens. The contract's 'Intent' frames this as a purely verbatim, name-preserving copy and never addresses this conflict — the programmer is left to silently violate an explicit repo-wide naming rule or silently rename a file the contract calls 'byte-for-byte identical', neither of which the contract authorizes.\n2. Point 9's acceptance criteria (8 tests passing) are not achievable as written without a Python environment that has openpyxl, pandas, and requests installed (confirmed via source/project/pyproject.toml's dependency list and by reading send_sms.py's and test_send_sms.py's actual imports) — none of which are in the repository's root requirements.txt (the framework's own shared environment). Current State, Inputs, and the points say nothing about how this environment is obtained (installing into the shared framework venv, using source/project/.venv, or creating a new project-scoped venv are all live options the contract leaves for the programmer to invent). Per PRINCIPLES.md P13, a real gap requiring an environment/dependency decision should be resolved by the contract, not improvised by the programmer.\n\nMinor, non-blocking note: Current State omits that source/project/README.md exists (confirmed present via filesystem and memory/CURRENT_STATE.md); it does not cause ambiguity here since the Outputs list is an exhaustive, closed set and Out of Scope already excludes project/README.md content, but it is a small P6 completeness gap worth the architect tightening while revising the other two points."
    },
    {
      "round": 2,
      "date": "2026-08-18T12:05:27+02:00",
      "verdict": "CHANGES_REQUESTED",
      "reviewer": "reviewer",
      "findings": "Checked the current contract text against AGENTS.md (project/ vs source/ scoping, ADR-024 read-only rule, ADR-008 naming convention, root .gitignore fixed-file-set rule), memory/DECISIONS.md (ADR-016, ADR-022, ADR-024, ADR-028/ADR-029's decision-1/decision-9 reviewer model, decision 7's risk criteria), the actual repository contents (source/project/* file inventory, source/project/pyproject.toml's dependency list, send_sms.py's and tests/test_send_sms.py's actual imports, config.example.toml's placeholder-only content, root .gitignore, root requirements.txt), and — new in this round — the actual programmer/reviewer/architect permission mechanics in agents/agent.py and each agent's config.json.\n\nFirst, verified that this round's two structural gaps are now genuinely resolved in the current point text, not just claimed: Point 7 now explicitly states the ADR-008 hyphen-to-underscore rationale for renaming SESSION_2026-04-10.md to SESSION_2026_04_10.md and adds an explicit criterion that no hyphenated file is created — resolves the earlier naming-convention gap. Points 9-11 now explicitly own the dependency-environment question (project-scoped project/.venv, install of openpyxl/pandas/requests/streamlit, matching project/pyproject.toml's actual declared constraints which I independently re-verified against the file and against send_sms.py's/test_send_sms.py's real import statements) instead of leaving it for the programmer to invent — resolves the earlier P13 gap in principle.\n\nHowever, direct verification of the tool-permission mechanics surfaces a new, concrete, blocking problem that was not present in round 1's findings: agents/programmer/config.json sets permission_profile 'edit' and provider 'claude'; agents/agent.py's _claude_permissions() maps 'edit' to CLAUDE_EDIT_TOOLS = (Read, Grep, Glob, Edit, Write) — no Bash tool at all (Bash is only granted under CLAUDE_FULL_TOOLS, i.e. permission_profile 'full', which no agent in this pipeline uses; architect and reviewer both use 'review', which is Read/Grep/Glob only, even more restricted). This means the programmer has no mechanism to execute a shell command of any kind. Yet: Point 8's acceptance criteria requires running `git check-ignore project/config.toml`; Point 9 requires `python -m venv`, then `pip show` to verify installed versions; Point 10 requires invoking `project/.venv/Scripts/python -m unittest discover ...`; Point 11 requires `git status`/`git diff`. None of these are achievable through Read/Grep/Glob/Edit/Write. Points 1-7 (verbatim file copies via Read+Write) are fine and require no shell access. This is exactly the check the reviewer is asked to make ('does the contract require destructive commands or access beyond the programmer profile (edit)?') — the answer for points 8-11 as currently worded is yes, and it is a real capability gap, not a hypothesis: confirmed by reading agents/agent.py's tool-mapping code and every agent's config.json directly.\n\nThis is fixable by rewriting, not an architecturally wrong request as a whole (the migration itself, and the underlying need for a project-scoped venv and gitignore entry, both remain sound and necessary) — hence CHANGES_REQUESTED, not REJECTED. The architect needs to either (a) rework points 8-11's acceptance criteria so verification does not depend on Bash-tool command execution the programmer cannot perform (e.g. state the intended git/pip/venv commands as instructions for the human owner to run and confirm outside the automated contract points, mirroring how every existing ADR's own 'Verification: python -m pytest -q — N/N passing' line in memory/DECISIONS.md was clearly performed by a human, not an agent tool call), or (b) explicitly scope points 9-10 out of this contract and hand dependency installation/test execution to the owner as a documented manual follow-up, keeping only the achievable Write-tool actions (the .gitignore edit itself in point 8, minus its git check-ignore verification step) inside the programmer's actual points.\n\nRisk_level: independently re-verified as correctly 'standard' — config.example.toml (re-read directly) contains only placeholder values (example gateway host, example UNC path, dummy phone numbers/passwords '1234'), no real credentials are copied or introduced, and the FakeClient-based test suite makes no real network calls. A pip install against the public PyPI registry (needed if point 9 survives revision) is routine dependency tooling, not the kind of 'real call to an external system' decision 7's criteria target (business/API integration, not package installation) — no escalation warranted on that basis alone."
    },
    {
      "round": 3,
      "date": "2026-08-18T12:44:25+02:00",
      "verdict": "ACCEPTED",
      "reviewer": "reviewer",
      "findings": "Independently re-verified this contract (round 3, fresh thread per Tr5-base decision 9) against AGENTS.md, memory/DECISIONS.md (ADR-008, ADR-016, ADR-022, ADR-024, ADR-029, decision 7's risk criteria), and the live repository state — not against the prior two rounds' text alone. Both blocking gaps from rounds 1 and 2 are genuinely resolved in the current point text: (1) Point 7 now renames SESSION_2026-04-10.md to SESSION_2026_04_10.md with the ADR-008 rationale stated and an explicit no-hyphenated-file criterion; independently confirmed all 7 other output filenames (send_sms.py, main.py, streamlit_app.py, pyproject.toml, config.example.toml, tests/test_send_sms.py) are already lowercase_with_underscores, no hyphens/diacritics. (2) Re-read agents/agent.py directly: CLAUDE_EDIT_TOOLS = (Read, Grep, Glob, Edit, Write), no Bash, matching agents/programmer/config.json's permission_profile 'edit'. Point 8's acceptance criteria now read the updated .gitignore via Read rather than `git check-ignore`, and Point 9 verifies via Glob listing rather than `git status`/`git diff` — all 9 points are achievable with Read/Grep/Glob/Edit/Write alone, no Bash-dependent step remains. Out of Scope now explicitly excludes venv creation, dependency install, and test execution as a documented manual owner follow-up, closing the earlier P13 environment-decision gap rather than leaving it for the programmer to invent. Fresh-filesystem verification of Current State's claims: project/ contains only the placeholder README.md; source/project/ contains exactly the 9 items Point 9 enumerates (verified via Glob); project/tests/ does not yet exist (Point 6 correctly creates it); root .gitignore has no config.toml entry and already has an unanchored .venv/ pattern; root requirements.txt lacks openpyxl/pandas/requests/streamlit, which are confirmed real imports in send_sms.py/main.py/streamlit_app.py and declared in source/project/pyproject.toml. risk_level 'standard' independently re-verified against decision 7's criteria: config.example.toml (read directly) contains placeholder-only values, SESSION_2026-04-10.md (read directly) contains no personal/real data, and tests/test_send_sms.py (read directly) uses a FakeClient with no real network calls — no escalation warranted. Out of Scope is explicit and complete: source/ untouched, project/README.md untouched (deferred to Contract 0001's revision), no project/.gitignore, no behavior changes. Point 8's root-.gitignore edit is correctly scoped as its own explicit point per ADR-022's 'a change outside project/ needs its own contract point' rule. No backward-compatibility issue (project/ was an empty placeholder). Both prior review-round lessons are already recorded in memory/DECISIONS.md (2026-08-18T11:49:50+02:00 and 2026-08-18T12:05:37+02:00 entries) — no duplicate entry needed. The contract is complete, actionable, verifiable, and within the programmer's actual tool access; it may proceed to implementation."
    }
  ],
  "completion_notes": "",
  "implementation_review_rounds": []
}
CONTRACT-META -->
