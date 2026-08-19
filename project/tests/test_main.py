from __future__ import annotations

import contextlib
import io
from pathlib import Path
import unittest
from unittest.mock import patch

import main
from send_sms import (
    DEFAULT_SEND_TIMEOUT,
    ConfigurationError,
    SmsResult,
    SpreadsheetError,
)


def _run_main(argv: list[str]) -> int:
    with contextlib.redirect_stdout(io.StringIO()):
        return main.main(argv)


class BuildParserTests(unittest.TestCase):
    def test_send_defaults_and_required_fields(self) -> None:
        parser = main.build_parser()
        args = parser.parse_args(["send", "--phone", "+420601060959", "--message", "Ahoj"])

        self.assertEqual(args.command, "send")
        self.assertEqual(args.phone, "+420601060959")
        self.assertEqual(args.message, "Ahoj")
        self.assertEqual(args.timeout, DEFAULT_SEND_TIMEOUT)
        self.assertEqual(args.config, Path("config.toml"))
        self.assertFalse(args.verbose)

    def test_send_requires_phone_and_message(self) -> None:
        parser = main.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["send", "--message", "Ahoj"])
            with self.assertRaises(SystemExit):
                parser.parse_args(["send", "--phone", "+420601060959"])

    def test_send_timeout_override(self) -> None:
        parser = main.build_parser()
        args = parser.parse_args(
            ["send", "--phone", "+420601060959", "--message", "Ahoj", "--timeout", "5.5"]
        )
        self.assertEqual(args.timeout, 5.5)

    def test_send_batch_defaults(self) -> None:
        parser = main.build_parser()
        args = parser.parse_args(["send-batch", "--gate", "1"])

        self.assertEqual(args.command, "send-batch")
        self.assertEqual(args.gate, 1)
        self.assertEqual(args.batch_size, 10)
        self.assertEqual(args.pause_seconds, 45.0)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.continue_on_error)
        self.assertEqual(args.timeout, DEFAULT_SEND_TIMEOUT)

    def test_send_batch_requires_gate(self) -> None:
        parser = main.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["send-batch"])

    def test_send_batch_timeout_override(self) -> None:
        parser = main.build_parser()
        args = parser.parse_args(["send-batch", "--gate", "1", "--timeout", "3"])
        self.assertEqual(args.timeout, 3.0)

    def test_supplement_defaults(self) -> None:
        parser = main.build_parser()
        args = parser.parse_args(["supplement", "--gate", "2"])

        self.assertEqual(args.command, "supplement")
        self.assertEqual(args.gate, 2)
        self.assertEqual(args.batch_size, 10)
        self.assertEqual(args.pause_seconds, 45.0)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.continue_on_error)
        self.assertEqual(args.timeout, DEFAULT_SEND_TIMEOUT)

    def test_supplement_requires_gate(self) -> None:
        parser = main.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["supplement"])

    def test_supplement_timeout_override(self) -> None:
        parser = main.build_parser()
        args = parser.parse_args(["supplement", "--gate", "2", "--timeout", "7"])
        self.assertEqual(args.timeout, 7.0)

    def test_find_one_defaults(self) -> None:
        parser = main.build_parser()
        args = parser.parse_args(["find-one", "--gate", "1", "--number", "777530100"])

        self.assertEqual(args.command, "find-one")
        self.assertEqual(args.gate, 1)
        self.assertEqual(args.number, "777530100")
        self.assertFalse(args.dry_run)
        self.assertEqual(args.timeout, DEFAULT_SEND_TIMEOUT)

    def test_find_one_requires_gate_and_number(self) -> None:
        parser = main.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["find-one", "--number", "777530100"])
            with self.assertRaises(SystemExit):
                parser.parse_args(["find-one", "--gate", "1"])

    def test_find_one_timeout_override(self) -> None:
        parser = main.build_parser()
        args = parser.parse_args(
            ["find-one", "--gate", "1", "--number", "777530100", "--timeout", "2"]
        )
        self.assertEqual(args.timeout, 2.0)

    def test_find_sheet_defaults(self) -> None:
        parser = main.build_parser()
        args = parser.parse_args(["find-sheet", "--gate", "1"])

        self.assertEqual(args.command, "find-sheet")
        self.assertEqual(args.gate, 1)
        self.assertEqual(args.pause_seconds, 20.0)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.continue_on_error)
        self.assertEqual(args.timeout, DEFAULT_SEND_TIMEOUT)

    def test_find_sheet_requires_gate(self) -> None:
        parser = main.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["find-sheet"])

    def test_find_sheet_timeout_override(self) -> None:
        parser = main.build_parser()
        args = parser.parse_args(["find-sheet", "--gate", "1", "--timeout", "9"])
        self.assertEqual(args.timeout, 9.0)

    def test_duplicates_defaults(self) -> None:
        parser = main.build_parser()
        args = parser.parse_args(["duplicates", "--gate", "1"])

        self.assertEqual(args.command, "duplicates")
        self.assertEqual(args.gate, 1)
        self.assertFalse(hasattr(args, "timeout"))

    def test_duplicates_requires_gate(self) -> None:
        parser = main.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["duplicates"])

    def test_duplicates_rejects_timeout(self) -> None:
        parser = main.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["duplicates", "--gate", "1", "--timeout", "5"])


class MainDispatchTests(unittest.TestCase):
    def test_send_returns_zero_on_success(self) -> None:
        with patch.object(main, "poslat_sms") as mock_send:
            mock_send.return_value = {
                "ok": True,
                "phone": "+420601060959",
                "message": "Ahoj",
                "status_code": 200,
                "payload": {},
                "error": None,
            }
            exit_code = _run_main(["send", "--phone", "+420601060959", "--message", "Ahoj"])

        self.assertEqual(exit_code, 0)
        mock_send.assert_called_once_with(
            "+420601060959",
            "Ahoj",
            config_path=Path("config.toml"),
            timeout=DEFAULT_SEND_TIMEOUT,
        )

    def test_send_returns_one_on_failure(self) -> None:
        with patch.object(main, "poslat_sms") as mock_send:
            mock_send.return_value = {
                "ok": False,
                "phone": "+420601060959",
                "message": "Ahoj",
                "status_code": 500,
                "payload": None,
                "error": "gateway error",
            }
            exit_code = _run_main(["send", "--phone", "+420601060959", "--message", "Ahoj"])

        self.assertEqual(exit_code, 1)

    def test_send_batch_returns_zero_on_success(self) -> None:
        with patch.object(main, "poslat_davkove_sms") as mock_batch:
            mock_batch.return_value = [SmsResult(ok=True, phone="+420601060959", message="A")]
            exit_code = _run_main(["send-batch", "--gate", "1"])

        self.assertEqual(exit_code, 0)
        mock_batch.assert_called_once_with(
            1,
            batch_size=10,
            pause_seconds=45.0,
            dry_run=False,
            stop_on_error=True,
            config_path=Path("config.toml"),
            timeout=DEFAULT_SEND_TIMEOUT,
        )

    def test_send_batch_returns_one_on_failure(self) -> None:
        with patch.object(main, "poslat_davkove_sms") as mock_batch:
            mock_batch.return_value = [
                SmsResult(ok=True, phone="+420601060959", message="A"),
                SmsResult(ok=False, phone="+420601060959", message="B", error="x"),
            ]
            exit_code = _run_main(["send-batch", "--gate", "1", "--continue-on-error"])

        self.assertEqual(exit_code, 1)
        mock_batch.assert_called_once_with(
            1,
            batch_size=10,
            pause_seconds=45.0,
            dry_run=False,
            stop_on_error=False,
            config_path=Path("config.toml"),
            timeout=DEFAULT_SEND_TIMEOUT,
        )

    def test_supplement_returns_zero_on_success(self) -> None:
        with patch.object(main, "doplneni_seznamu_zavor") as mock_supplement:
            mock_supplement.return_value = [SmsResult(ok=True, phone="+420601060959", message="A")]
            exit_code = _run_main(["supplement", "--gate", "2", "--dry-run"])

        self.assertEqual(exit_code, 0)
        mock_supplement.assert_called_once_with(
            2,
            batch_size=10,
            pause_seconds=45.0,
            dry_run=True,
            stop_on_error=True,
            config_path=Path("config.toml"),
            timeout=DEFAULT_SEND_TIMEOUT,
        )

    def test_supplement_returns_one_on_failure(self) -> None:
        with patch.object(main, "doplneni_seznamu_zavor") as mock_supplement:
            mock_supplement.return_value = [
                SmsResult(ok=False, phone="+420601060959", message="A", error="x"),
            ]
            exit_code = _run_main(["supplement", "--gate", "2"])

        self.assertEqual(exit_code, 1)

    def test_find_one_returns_zero_on_success(self) -> None:
        with patch.object(main, "najit_cislo_na_zavore") as mock_find_one:
            mock_find_one.return_value = SmsResult(ok=True, phone="+420601060959", message="FIND")
            exit_code = _run_main(["find-one", "--gate", "1", "--number", "777530100"])

        self.assertEqual(exit_code, 0)
        mock_find_one.assert_called_once_with(
            1,
            "777530100",
            dry_run=False,
            config_path=Path("config.toml"),
            timeout=DEFAULT_SEND_TIMEOUT,
        )

    def test_find_one_returns_one_on_failure(self) -> None:
        with patch.object(main, "najit_cislo_na_zavore") as mock_find_one:
            mock_find_one.return_value = SmsResult(
                ok=False, phone="+420601060959", message="FIND", error="x"
            )
            exit_code = _run_main(["find-one", "--gate", "1", "--number", "777530100"])

        self.assertEqual(exit_code, 1)

    def test_find_sheet_returns_zero_on_success(self) -> None:
        with patch.object(main, "najit_cisla_ze_seznamu_na_zavore") as mock_find_sheet:
            mock_find_sheet.return_value = [SmsResult(ok=True, phone="+420601060959", message="FIND")]
            exit_code = _run_main(["find-sheet", "--gate", "1"])

        self.assertEqual(exit_code, 0)
        mock_find_sheet.assert_called_once_with(
            1,
            pause_seconds=20.0,
            dry_run=False,
            stop_on_error=True,
            config_path=Path("config.toml"),
            timeout=DEFAULT_SEND_TIMEOUT,
        )

    def test_find_sheet_returns_one_on_failure(self) -> None:
        with patch.object(main, "najit_cisla_ze_seznamu_na_zavore") as mock_find_sheet:
            mock_find_sheet.return_value = [
                SmsResult(ok=False, phone="+420601060959", message="FIND", error="x")
            ]
            exit_code = _run_main(["find-sheet", "--gate", "1"])

        self.assertEqual(exit_code, 1)

    def test_duplicates_returns_zero_regardless_of_result(self) -> None:
        with patch.object(main, "najit_duplikaty") as mock_duplicates:
            mock_duplicates.return_value = ["+420601060959", "+420601060959"]
            exit_code = _run_main(["duplicates", "--gate", "1"])

        self.assertEqual(exit_code, 0)
        mock_duplicates.assert_called_once_with(1, config_path=Path("config.toml"))

    def test_duplicates_returns_zero_when_empty(self) -> None:
        with patch.object(main, "najit_duplikaty") as mock_duplicates:
            mock_duplicates.return_value = []
            exit_code = _run_main(["duplicates", "--gate", "1"])

        self.assertEqual(exit_code, 0)

    def test_configuration_error_returns_two(self) -> None:
        with patch.object(main, "poslat_sms") as mock_send:
            mock_send.side_effect = ConfigurationError("missing config")
            exit_code = _run_main(["send", "--phone", "+420601060959", "--message", "Ahoj"])

        self.assertEqual(exit_code, 2)

    def test_spreadsheet_error_returns_two(self) -> None:
        with patch.object(main, "poslat_davkove_sms") as mock_batch:
            mock_batch.side_effect = SpreadsheetError("bad sheet")
            exit_code = _run_main(["send-batch", "--gate", "1"])

        self.assertEqual(exit_code, 2)

    def test_value_error_returns_two(self) -> None:
        with patch.object(main, "najit_cislo_na_zavore") as mock_find_one:
            mock_find_one.side_effect = ValueError("bad number")
            exit_code = _run_main(["find-one", "--gate", "1", "--number", "abc"])

        self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()
