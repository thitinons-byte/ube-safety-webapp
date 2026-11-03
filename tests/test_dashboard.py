import csv
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest
from src.storage import CSV_COLUMNS


APP_PATH = Path(__file__).resolve().parent.parent / "app.py"


def complete_columns(frame):
    for column in CSV_COLUMNS:
        if column not in frame:
            frame[column] = ""
    return frame.loc[:, CSV_COLUMNS]


class DashboardTests(unittest.TestCase):
    def test_real_reports_show_four_metrics_without_demo(self):
        reports = complete_columns(pd.DataFrame(
            {"report_id": ["ST-1", "ST-2"], "talk_date": ["4/11/2026", "2026-12-05"],
             "company": ["UBE", "UBS"], "department": ["ผลิต", "ซ่อมบำรุง"],
             "participants": [3, 5]}
        ))
        with patch("pandas.read_csv", return_value=reports) as read_csv, patch("streamlit.bar_chart") as chart:
            app = AppTest.from_file(str(APP_PATH)).run()
            next(button for button in app.button if button.key == "menu_Dashboard").click().run()
        self.assertEqual(read_csv.call_count, 1)
        self.assertEqual([metric.value for metric in app.metric], ["2", "8", "1", "1"])
        self.assertEqual(chart.call_count, 1)
        self.assertEqual(
            chart.call_args.args[0].to_dict("records"),
            [{"เดือน": "2026-11", "จำนวนกิจกรรม": 1},
             {"เดือน": "2026-12", "จำนวนกิจกรรม": 1}],
        )
        self.assertEqual(len(app.warning), 0)
        self.assertEqual(len(app.exception), 0)

    def test_empty_reports_use_labeled_demo_sample(self):
        empty = complete_columns(pd.DataFrame(columns=CSV_COLUMNS))
        sample = complete_columns(pd.DataFrame(
            {"report_id": ["ST-DEMO"], "talk_date": ["6/9/2026"],
             "company": ["UBE"], "department": ["ผลิต"], "participants": [12]}
        ))
        with patch("pandas.read_csv", side_effect=[empty, sample]) as read_csv, patch("streamlit.bar_chart") as chart:
            app = AppTest.from_file(str(APP_PATH)).run()
            next(button for button in app.button if button.key == "menu_Dashboard").click().run()
        self.assertEqual(read_csv.call_count, 2)
        self.assertEqual([metric.value for metric in app.metric], ["1", "12", "1", "0"])
        self.assertIn("DEMO", app.warning[0].value)
        self.assertEqual(chart.call_args.args[0]["เดือน"].tolist(), ["2026-09"])
        self.assertEqual(len(app.exception), 0)

    def test_invalid_dates_do_not_draw_chart(self):
        reports = complete_columns(pd.DataFrame(
            {"report_id": ["ST-1"], "talk_date": ["ไม่ใช่วันที่"],
             "company": ["UBE"], "department": ["ผลิต"], "participants": [2]}
        ))
        with patch("pandas.read_csv", return_value=reports), patch("streamlit.bar_chart") as chart:
            app = AppTest.from_file(str(APP_PATH)).run()
            next(button for button in app.button if button.key == "menu_Dashboard").click().run()
        chart.assert_not_called()
        self.assertEqual(len(app.info), 1)
        self.assertEqual(len(app.exception), 0)

    def test_empty_demo_sample_does_not_draw_chart(self):
        empty = complete_columns(pd.DataFrame(columns=CSV_COLUMNS))
        with patch("pandas.read_csv", side_effect=[empty, empty]), patch("streamlit.bar_chart") as chart:
            app = AppTest.from_file(str(APP_PATH)).run()
            next(button for button in app.button if button.key == "menu_Dashboard").click().run()
        chart.assert_not_called()
        self.assertEqual([metric.value for metric in app.metric], ["0", "0", "0", "0"])
        self.assertIn("DEMO", app.warning[0].value)

    def test_all_filters_update_kpis_and_chart_and_reset_department(self):
        reports = complete_columns(pd.DataFrame(
            {
                "report_id": ["ST-1", "ST-2", "ST-3", "ST-4"],
                "talk_date": ["2026-11-01", "2026-12-01", "2026-11-02", "2025-11-03"],
                "company": ["UBE", "UBE", "UBS", "UBS"],
                "department": ["ผลิต", "ซ่อมบำรุง", "คลังสินค้า", "คลังสินค้า"],
                "participants": [2, 3, 5, 7],
            }
        ))
        with (patch("pandas.read_csv", return_value=reports),
              patch("streamlit.bar_chart") as chart,
              patch("streamlit.download_button") as download):
            app = AppTest.from_file(str(APP_PATH)).run()
            next(button for button in app.button if button.key == "menu_Dashboard").click().run()
            app.selectbox(key="dashboard_company").select("UBE").run()
            self.assertEqual(app.selectbox(key="dashboard_department").options, ["ทั้งหมด", "ผลิต", "ซ่อมบำรุง"])
            app.selectbox(key="dashboard_department").select("ผลิต").run()
            app.selectbox(key="dashboard_year").select(2026).run()
            app.selectbox(key="dashboard_month").select(11).run()
            self.assertEqual([metric.value for metric in app.metric], ["1", "2", "1", "0"])
            self.assertEqual(chart.call_args.args[0].to_dict("records"),
                             [{"เดือน": "2026-11", "จำนวนกิจกรรม": 1}])
            export = download.call_args.kwargs
            self.assertTrue(export["data"].startswith(b"\xef\xbb\xbf"))
            self.assertRegex(export["file_name"], r"^SafetyTalk_\d{8}\.csv$")
            reader = csv.DictReader(StringIO(export["data"].decode("utf-8-sig")))
            self.assertEqual(reader.fieldnames, CSV_COLUMNS)
            self.assertEqual([row["report_id"] for row in reader], ["ST-1"])
            app.selectbox(key="dashboard_company").select("UBS").run()
            self.assertEqual(app.selectbox(key="dashboard_department").value, "ทั้งหมด")
            self.assertEqual(app.selectbox(key="dashboard_department").options,
                             ["ทั้งหมด", "คลังสินค้า"])
            self.assertEqual([metric.value for metric in app.metric], ["1", "5", "0", "1"])
            app.selectbox(key="dashboard_year").select(2025).run()
            self.assertEqual([metric.value for metric in app.metric], ["1", "7", "0", "1"])
            app.selectbox(key="dashboard_month").select(12).run()
            self.assertEqual([metric.value for metric in app.metric], ["0", "0", "0", "0"])
            self.assertTrue(app.info)
            self.assertTrue(download.call_args.kwargs["disabled"])
        self.assertEqual(len(app.exception), 0)


if __name__ == "__main__":
    unittest.main()
