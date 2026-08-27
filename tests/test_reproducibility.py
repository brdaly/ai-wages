import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReproducibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp_dir.cleanup)
        cls.worktree = Path(cls.temp_dir.name) / "ai-wages"
        shutil.copytree(
            ROOT,
            cls.worktree,
            ignore=shutil.ignore_patterns(".git", "__pycache__"),
        )
        cls.completed = subprocess.run(
            [sys.executable, "analysis.py"],
            cwd=cls.worktree,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.results = json.loads((cls.worktree / "results.json").read_text())

    def test_analysis_reports_expected_sample(self):
        self.assertIn("Occupations matched", self.completed.stdout)
        self.assertEqual(self.results["n_occupations"], 454)

    def test_headline_statistics_match_committed_data(self):
        self.assertEqual(self.results["pearson_wage_exposure"], 0.197)
        self.assertEqual(self.results["spearman_wage_exposure"], 0.333)
        self.assertAlmostEqual(
            self.results["augmentation_share"]
            + self.results["automation_share"],
            1.0,
            places=3,
        )

    def test_quintiles_cover_the_full_sample(self):
        quintiles = self.results["by_wage_quintile"]
        self.assertEqual(len(quintiles), 5)
        self.assertEqual(
            sum(quintile["n"] for quintile in quintiles),
            self.results["n_occupations"],
        )

    def test_figure_is_regenerated(self):
        figure = self.worktree / "figures" / "ai_exposure_wage.png"
        self.assertTrue(figure.is_file())
        self.assertGreater(figure.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
