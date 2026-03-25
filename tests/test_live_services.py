import tempfile
import unittest
from pathlib import Path

from dashboard import build_dashboard_payload
from main import SUBJECTS, main as run_main
from ytl import LETTERS


class LiveServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_ytl_subject_returns_live_point_rows(self):
        subject = next(subject for subject in SUBJECTS if subject.name == "Matematiikka (pitkä)")
        _, ytl_results = await run_main(subjects=[subject], output_path=Path(tempfile.gettempdir()) / "unused-dashboard.html")

        self.assertTrue(ytl_results, "Expected live YTL results")
        self.assertTrue(all(row.subject == subject.name for row in ytl_results))
        self.assertTrue(all(int(row.semester[:4]) >= 2021 for row in ytl_results))
        self.assertTrue(all(0 < row.value <= 1 for row in ytl_results))

        latest_semester = max({row.semester for row in ytl_results})
        latest_rows = [row for row in ytl_results if row.semester == latest_semester]
        self.assertEqual([row.grade for row in latest_rows], LETTERS)
        self.assertEqual(sorted((row.value for row in latest_rows), reverse=True), [row.value for row in latest_rows])

    async def test_live_results_build_dashboard_payload(self):
        subject = next(subject for subject in SUBJECTS if subject.name == "Matematiikka (pitkä)")
        _, ytl_results = await run_main(subjects=[subject], output_path=Path(tempfile.gettempdir()) / "unused-dashboard.html")

        payload = build_dashboard_payload([subject], ytl_results)

        self.assertIn(subject.name, payload["subjects"])
        self.assertTrue(payload["subjects"][subject.name]["grades"]["L"])
        self.assertTrue(payload["subjects"][subject.name]["availability"]["semesters"])


if __name__ == "__main__":
    unittest.main()
