# Project

## Purpose

Holds the actual, migrated application code for the SMS gateway helper
project: a CLI and Streamlit tool for managing GSM gate phone number lists
over an SMS gateway (adding, finding, and de-duplicating numbers stored in
Excel gate sheets). This directory is kept separate from the agentic
framework/governance layer that lives at the repository root
(`chat_architect.py`, `agents/agent.py`, `agents/agent_profile.py`,
`agents/contract_workflow.py`, `agents/git_ops.py`, `agents/pipeline.py`,
`agents/voice.py`, `agents/<name>/`, `tools/discovery_engine/`,
`templates/voice_module/`, `memory/`, `contracts/`, `AGENTS.md`,
`PRINCIPLES.md`). Every implementation contract's actual code changes land
here. The project's original source, prior to migration, lives in
`source/` (untouched, read-only reference) — see ADR-024.

## Current capabilities (v0.1)

- `send_sms.py` — core logic: TOML config loading, phone number
  normalization/validation, sheet analysis (duplicate and invalid row
  detection), the `SmsGatewayClient` used to talk to the SMS gateway, and
  safe in-place Excel writes (temp file + atomic replace, with an optional
  timestamped backup copy).
- Concurrent saves to the shared Excel workbook are detected and safely
  rejected, not silently overwritten: `save_sheet_numbers()` creates a
  sidecar `<workbook>.lock` file before reading the workbook, and any
  overlapping save attempt fails with a clear error instead of racing the
  first one.
- `main.py` — command-line interface with six subcommands: `send`
  (send one SMS to an arbitrary number), `send-batch` (send ADD commands
  from a gate sheet), `supplement` (send ADD commands from the "Doplnit"
  sheet), `find-one` (send one FIND command), `find-sheet` (send FIND
  commands for all numbers in a sheet), and `duplicates` (list duplicate
  phone numbers in a gate sheet). The five SMS-sending subcommands (`send`,
  `send-batch`, `supplement`, `find-one`, `find-sheet`) accept a
  `--timeout` option for the HTTP timeout used when talking to the SMS
  gateway, matching the Streamlit UI's per-operation timeout input.
- `streamlit_app.py` — web UI: sheet overview, an inline editor that saves
  changes back to the Excel workbook, batch ADD/FIND operations, one-off
  SMS sending, and data quality checks.
- `tests/test_send_sms.py` — unit tests for the core logic in
  `send_sms.py`; the full suite (8 tests) has been confirmed passing by
  the owner after installing dependencies.
- `tests/test_main.py` — unit tests for `main.py`'s argument parsing
  (`build_parser()`, all six subcommands) and dispatch logic (`main()`,
  invoked via its `argv` parameter with each of the six `send_sms`
  functions mocked, so no real network or file I/O occurs).
- `tests/test_streamlit_app.py` — unit tests for `streamlit_app.py`'s
  pure, non-UI data-transformation helper functions (`gate_label`,
  `rows_dataframe`, `editable_numbers_dataframe`, `messages_dataframe`,
  `results_dataframe`).
- `config.example.toml` — configuration template for the gateway
  credentials and gate sheet definitions.
- Each gate's phone-number column is configurable per gate via an optional
  `phone_column_index` field on its `[[gates]]` entry in `config.toml`;
  when omitted, it defaults to the prior hardcoded column index, so an
  existing `config.toml` without the field keeps working unchanged.

### Development environment

`project/.venv` is a project-scoped Python virtual environment, separate
from the repository's root framework environment (which holds
`openai-codex`, `claude-agent-sdk`, `python-dotenv`, `pytest`, `pyaudio`,
`google-genai`). It is gitignored (covered by the root `.gitignore`'s
existing unanchored `.venv/` pattern) rather than a versioned deliverable,
and was created and populated manually by the project owner — the
programmer agent has no shell access to do this itself. Its dependencies
(`openpyxl`, `pandas`, `requests`, `streamlit`) come from
`project/pyproject.toml`. Example usage on Windows:

```
project\.venv\Scripts\python.exe -m pip install openpyxl pandas requests streamlit
project\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Running the application for real also requires a local
`project/config.toml`, copied from `config.example.toml` and filled in
with real gateway/gate details; `config.toml` is itself gitignored per the
root `.gitignore`'s `config.toml` entry.

## Current limitations

- `streamlit_app.py`'s Streamlit-dependent rendering/interaction code
  (its tabs, forms, session-state handling, widgets, and `main()` itself)
  remains untested; covering it would require a dedicated harness such as
  `streamlit.testing.v1.AppTest` and is deferred to a possible future
  contract, not attempted here.
- A `<workbook>.lock` file left behind by a process that crashes mid-save
  is not automatically cleared (no staleness/TTL recovery); such a lock
  would need to be removed manually before further saves can succeed.

## Planned evolution

- Grows as further contracts are implemented. Resolving the limitations
  listed above — concurrent-write protection, CLI/UI parameter parity,
  per-gate column configuration, and additional test coverage — is
  deferred to those future contracts, not addressed here. Internal
  structure is decided when a real need for it actually arises, not in
  advance (see `PRINCIPLES.md` P1, P15).
