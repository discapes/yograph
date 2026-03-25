import tempfile
import unittest
from pathlib import Path

from dashboard import build_dashboard_payload, render_dashboard_html, save_dashboard_html, semester_sort_key
from lib import Subject, YtlDatum
from main import output_csv


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.subjects = [
            Subject("Fysiikka", "Fysiikka", 120),
            Subject("Kemia", "Kemia", 120),
        ]

    def test_semester_sort_key_orders_chronologically(self):
        semesters = ["2025 syksy", "2024 syksy", "2025 kevät", "2024 kevät"]
        self.assertEqual(sorted(semesters, key=semester_sort_key), ["2024 kevät", "2024 syksy", "2025 kevät", "2025 syksy"])

    def test_build_dashboard_payload_groups_thresholds_by_grade(self):
        ytl_results = [
            YtlDatum("2024 kevät", "Fysiikka", "L", 0.9),
            YtlDatum("2024 syksy", "Fysiikka", "L", 0.8),
            YtlDatum("2024 kevät", "Fysiikka", "E", 0.75),
            YtlDatum("2024 kevät", "Kemia", "L", 0.7),
        ]

        payload = build_dashboard_payload(self.subjects, ytl_results)

        self.assertEqual(payload["subject_order"], ["Fysiikka", "Kemia"])
        self.assertEqual(payload["semesters"], ["2024 kevät", "2024 syksy"])
        self.assertEqual(payload["subjects"]["Fysiikka"]["grades"]["L"]["2024 syksy"], 0.8)
        self.assertEqual(payload["subjects"]["Fysiikka"]["availability"]["semester_count"], 2)
        self.assertEqual(payload["subjects"]["Fysiikka"]["availability"]["latest_semester"], "2024 syksy")
        self.assertEqual(payload["subjects"]["Kemia"]["availability"]["semesters"], ["2024 kevät"])

    def test_render_dashboard_html_contains_ytl_only_controls(self):
        payload = build_dashboard_payload(self.subjects, [])

        html = render_dashboard_html(payload, "2026-03-25 12:00:00 UTC")

        self.assertIn("<h1>YO_graph</h1>", html)
        self.assertIn('id="subject-select"', html)
        self.assertNotIn('id="grade-select"', html)
        self.assertNotIn('id="view-select"', html)
        self.assertNotIn('summary-title', html)
        self.assertNotIn("Latest Thresholds", html)
        self.assertNotIn("YLE", html.split("<script")[0])

    def test_save_dashboard_html_writes_file(self):
        payload = build_dashboard_payload(self.subjects, [])

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = save_dashboard_html(Path(tmp_dir) / "dashboard.html", payload, "2026-03-25 12:00:00 UTC")
            self.assertTrue(path.exists())
            self.assertIn("<title>YO_graph</title>", path.read_text(encoding="utf-8"))

    def test_output_csv_writes_rows(self):
        rows = [YtlDatum("2024 kevät", "Fysiikka", "L", 0.9)]

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "out.csv"
            output_csv(rows, str(path))
            self.assertEqual(path.read_text().strip(), "semester,subject,grade,value\n2024 kevät,Fysiikka,L,0.9")

    def test_output_csv_rejects_empty_rows(self):
        with self.assertRaisesRegex(ValueError, "rows must not be empty"):
            output_csv([], "ignored.csv")


if __name__ == "__main__":
    unittest.main()
