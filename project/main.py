from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Sequence

from send_sms import (
    ConfigurationError,
    SpreadsheetError,
    doplneni_seznamu_zavor,
    najit_cisla_ze_seznamu_na_zavore,
    najit_cislo_na_zavore,
    najit_duplikaty,
    poslat_davkove_sms,
    poslat_sms,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SMS gateway helper for gate administration.")
    parser.add_argument("--config", type=Path, default=Path("config.toml"), help="Path to TOML config.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    send_parser = subparsers.add_parser("send", help="Send one SMS to an arbitrary number.")
    send_parser.add_argument("--phone", required=True, help="Recipient phone number.")
    send_parser.add_argument("--message", required=True, help="Message text.")

    batch_parser = subparsers.add_parser("send-batch", help="Send ADD commands from a gate sheet.")
    batch_parser.add_argument("--gate", required=True, type=int, help="Configured gate id.")
    batch_parser.add_argument("--batch-size", type=int, default=10, help="Phone numbers per ADD command.")
    batch_parser.add_argument("--pause-seconds", type=float, default=45.0, help="Delay between SMS sends.")
    batch_parser.add_argument("--dry-run", action="store_true", help="Build messages but do not send them.")
    batch_parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue sending even when one request fails.",
    )

    supplement_parser = subparsers.add_parser("supplement", help="Send ADD commands from sheet 'Doplnit'.")
    supplement_parser.add_argument("--gate", required=True, type=int, help="Configured gate id.")
    supplement_parser.add_argument("--batch-size", type=int, default=10, help="Phone numbers per ADD command.")
    supplement_parser.add_argument("--pause-seconds", type=float, default=45.0, help="Delay between SMS sends.")
    supplement_parser.add_argument("--dry-run", action="store_true", help="Build messages but do not send them.")
    supplement_parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue sending even when one request fails.",
    )

    find_one_parser = subparsers.add_parser("find-one", help="Send one FIND command.")
    find_one_parser.add_argument("--gate", required=True, type=int, help="Configured gate id.")
    find_one_parser.add_argument("--number", required=True, help="Phone number to search on the gate.")
    find_one_parser.add_argument("--dry-run", action="store_true", help="Build message but do not send it.")

    find_sheet_parser = subparsers.add_parser("find-sheet", help="Send FIND commands for all numbers in a sheet.")
    find_sheet_parser.add_argument("--gate", required=True, type=int, help="Configured gate id.")
    find_sheet_parser.add_argument("--pause-seconds", type=float, default=20.0, help="Delay between SMS sends.")
    find_sheet_parser.add_argument("--dry-run", action="store_true", help="Build messages but do not send them.")
    find_sheet_parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue sending even when one request fails.",
    )

    duplicates_parser = subparsers.add_parser("duplicates", help="List duplicate phone numbers in a gate sheet.")
    duplicates_parser.add_argument("--gate", required=True, type=int, help="Configured gate id.")

    return parser


def configure_logging(verbose: bool) -> None:
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def serialize_results(results: Sequence[object]) -> str:
    normalized = []
    for result in results:
        if hasattr(result, "__dict__"):
            normalized.append(result.__dict__)
        else:
            normalized.append(result)
    return json.dumps(normalized, ensure_ascii=False, indent=2)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging(args.verbose)

    try:
        if args.command == "send":
            payload = poslat_sms(args.phone, args.message, config_path=args.config)
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0 if payload["ok"] else 1

        if args.command == "send-batch":
            results = poslat_davkove_sms(
                args.gate,
                batch_size=args.batch_size,
                pause_seconds=args.pause_seconds,
                dry_run=args.dry_run,
                stop_on_error=not args.continue_on_error,
                config_path=args.config,
            )
            print(serialize_results(results))
            return 0 if all(result.ok for result in results) else 1

        if args.command == "supplement":
            results = doplneni_seznamu_zavor(
                args.gate,
                batch_size=args.batch_size,
                pause_seconds=args.pause_seconds,
                dry_run=args.dry_run,
                stop_on_error=not args.continue_on_error,
                config_path=args.config,
            )
            print(serialize_results(results))
            return 0 if all(result.ok for result in results) else 1

        if args.command == "find-one":
            result = najit_cislo_na_zavore(
                args.gate,
                args.number,
                dry_run=args.dry_run,
                config_path=args.config,
            )
            print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
            return 0 if result.ok else 1

        if args.command == "find-sheet":
            results = najit_cisla_ze_seznamu_na_zavore(
                args.gate,
                pause_seconds=args.pause_seconds,
                dry_run=args.dry_run,
                stop_on_error=not args.continue_on_error,
                config_path=args.config,
            )
            print(serialize_results(results))
            return 0 if all(result.ok for result in results) else 1

        if args.command == "duplicates":
            duplicates = najit_duplikaty(args.gate, config_path=args.config)
            print(json.dumps(duplicates, ensure_ascii=False, indent=2))
            return 0

        parser.error(f"Unsupported command: {args.command}")
    except (ConfigurationError, SpreadsheetError, ValueError) as exc:
        logging.error("%s", exc)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
