import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class AppSubmissionTests(unittest.TestCase):
    def test_permission_error_allows_retry(self):
        app_path = Path(__file__).resolve().parent.parent / "app.py"
        with patch(
            "src.storage.save_report",
            side_effect=[PermissionError("locked"), "ST-20261102-0001"],
        ) as save:
            app = AppTest.from_file(str(app_path)).run()
            app.selectbox[0].select("UBE").run()
            app.selectbox[1].select(app.selectbox[1].options[0])
            app.date_input[0].set_value(date(2026, 11, 2))
            app.text_input[0].set_value("ผู้สาธิต")
            app.text_input[1].set_value("หัวข้อทดสอบ")
            app.button[0].click().run()
            self.assertEqual(len(app.error), 1)
            self.assertIn("Excel", app.error[0].value)
            self.assertEqual(len(app.success), 0)
            app.button[0].click().run()
            self.assertEqual(len(app.success), 1)
            self.assertEqual(save.call_count, 2)

    def test_success_and_rerun_do_not_save_twice(self):
        app_path = Path(__file__).resolve().parent.parent / "app.py"
        with patch("src.storage.save_report", return_value="ST-20261102-0001") as save:
            app = AppTest.from_file(str(app_path)).run()
            app.selectbox[0].select("UBE").run()
            app.selectbox[1].select(app.selectbox[1].options[0])
            app.date_input[0].set_value(date(2026, 11, 2))
            app.text_input[0].set_value("ผู้สาธิต")
            app.text_input[1].set_value("หัวข้อทดสอบ")
            app.button[0].click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.success), 1)
            self.assertIn("ST-20261102-0001", app.success[0].value)
            self.assertEqual(save.call_count, 1)
            app.run()
            self.assertEqual(save.call_count, 1)


if __name__ == "__main__":
    unittest.main()
