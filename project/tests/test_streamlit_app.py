from __future__ import annotations

import json
import unittest

from send_sms import GateConfig, SheetAnalysis, SheetRow, SmsResult
import streamlit_app


def _build_analysis() -> SheetAnalysis:
    rows = [
        SheetRow(row_number=1, raw_value="777530100", normalized="+420777530100", status="valid"),
        SheetRow(row_number=2, raw_value="777530100", normalized="+420777530100", status="duplicate"),
        SheetRow(row_number=3, raw_value="abc", normalized=None, status="invalid", error="bad number"),
        SheetRow(row_number=4, raw_value="", normalized=None, status="blank"),
    ]
    return SheetAnalysis(
        source_name="sheet",
        rows=rows,
        valid_numbers=["+420777530100", "+420777530100"],
        unique_numbers=["+420777530100"],
        duplicate_numbers=["+420777530100"],
        invalid_rows=[rows[2]],
        blank_row_count=1,
    )


class GateLabelTests(unittest.TestCase):
    def test_gate_label_formats_id_and_sheet(self) -> None:
        gate = GateConfig(id=3, phone="+420601060959", password="2803", sheet="3 - Namesti")
        self.assertEqual(streamlit_app.gate_label(gate), "3: 3 - Namesti")


class RowsDataframeTests(unittest.TestCase):
    def test_rows_dataframe_has_expected_columns_and_rows(self) -> None:
        analysis = _build_analysis()
        dataframe = streamlit_app.rows_dataframe(analysis)

        self.assertEqual(
            list(dataframe.columns),
            ["radek", "puvodni_hodnota", "normalizovane_cislo", "stav", "chyba"],
        )
        self.assertEqual(len(dataframe), 4)
        self.assertEqual(dataframe.iloc[0]["stav"], "valid")
        self.assertEqual(dataframe.iloc[2]["chyba"], "bad number")

    def test_rows_dataframe_filters_by_statuses(self) -> None:
        analysis = _build_analysis()
        dataframe = streamlit_app.rows_dataframe(analysis, statuses=("valid", "duplicate"))

        self.assertEqual(len(dataframe), 2)
        self.assertTrue((dataframe["stav"].isin(["valid", "duplicate"])).all())


class EditableNumbersDataframeTests(unittest.TestCase):
    def test_editable_numbers_dataframe_excludes_blank_rows(self) -> None:
        analysis = _build_analysis()
        dataframe = streamlit_app.editable_numbers_dataframe(analysis)

        self.assertEqual(list(dataframe.columns), ["telefon"])
        self.assertEqual(len(dataframe), 3)
        self.assertEqual(
            dataframe["telefon"].tolist(),
            ["+420777530100", "+420777530100", "abc"],
        )


class MessagesDataframeTests(unittest.TestCase):
    def test_messages_dataframe_uses_one_based_order(self) -> None:
        messages = ["2803 ADD +420111111111", "2803 ADD +420222222222"]
        dataframe = streamlit_app.messages_dataframe(messages)

        self.assertEqual(list(dataframe.columns), ["poradi", "prikaz_sms"])
        self.assertEqual(dataframe["poradi"].tolist(), [1, 2])
        self.assertEqual(dataframe["prikaz_sms"].tolist(), messages)


class ResultsDataframeTests(unittest.TestCase):
    def test_results_dataframe_matches_columns_and_serializes_payload(self) -> None:
        results = [
            SmsResult(
                ok=True,
                phone="+420601060959",
                message="A",
                status_code=200,
                payload={"queued": True},
            ),
            SmsResult(
                ok=False,
                phone="+420602191729",
                message="B",
                status_code=500,
                error="gateway error",
            ),
        ]
        dataframe = streamlit_app.results_dataframe(results)

        self.assertEqual(
            list(dataframe.columns),
            ["ok", "telefon", "zprava", "status_code", "chyba", "odpoved"],
        )
        self.assertEqual(dataframe.iloc[0]["odpoved"], json.dumps({"queued": True}, ensure_ascii=False))
        self.assertEqual(dataframe.iloc[1]["odpoved"], "")
        self.assertEqual(dataframe.iloc[1]["chyba"], "gateway error")


if __name__ == "__main__":
    unittest.main()
