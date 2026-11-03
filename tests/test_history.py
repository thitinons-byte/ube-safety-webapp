import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parent.parent / "app.py"


def open_history():
    app = AppTest.from_file(str(APP_PATH)).run()
    next(button for button in app.button if button.key == "menu_ประวัติรายงาน").click().run()
    return app


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.reports = pd.DataFrame(
            {
                "report_id": ["ST-20261102-0001", "ST-20261103-0001", "ST-20261104-0001"],
                "company": ["UBE", "UBS", "UBE"],
                "reporter": ["ผู้สาธิต ก", "ผู้สาธิต ข", "ผู้สาธิต ค"],
                "topic": ["อัคคีภัย", "เครื่องจักร", "การเดิน"],
            }
        )

    def test_search_and_company_filter(self):
        with patch("pandas.read_csv", return_value=self.reports) as read_csv:
            app = open_history()
            self.assertEqual(len(app.dataframe[0].value), 3)
            app.text_input[0].set_value("เครื่องจักร").run()
            self.assertEqual(app.dataframe[0].value["company"].tolist(), ["UBS"])
            app.text_input[0].set_value("ST-20261102").run()
            self.assertEqual(app.dataframe[0].value["company"].tolist(), ["UBE"])
            app.text_input[0].set_value("").run()
            app.selectbox[0].select("UBS").run()
            self.assertEqual(app.dataframe[0].value["report_id"].tolist(), ["ST-20261103-0001"])
            app.text_input[0].set_value("ผู้สาธิต ก").run()
            self.assertEqual(len(app.dataframe), 0)
            self.assertTrue(app.info)
        self.assertTrue(all(call.args[0].name == "reports.csv" for call in read_csv.call_args_list))
        self.assertEqual(len(app.exception), 0)

    def test_empty_reports_show_explanation(self):
        with patch("pandas.read_csv", return_value=self.reports.iloc[0:0]) as read_csv:
            app = open_history()
        self.assertEqual(read_csv.call_count, 1)
        self.assertEqual(len(app.dataframe), 0)
        self.assertIn("ยังไม่มีรายงาน", app.info[0].value)
        self.assertEqual(len(app.exception), 0)


if __name__ == "__main__":
    unittest.main()
