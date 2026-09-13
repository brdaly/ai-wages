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

    def test_join_coverage_is_disclosed(self):
        """The inner join drops 40% of the index, so it has to be visible.

        The wage table is a legacy file with no row for 302 of the 756
        occupations the index reports. Dropping them is defensible; dropping
        them silently is not, because the unmatched set is on average the more
        AI-exposed one, which makes every reported level a lower bound.
        """
        coverage = self.results["coverage"]
        self.assertEqual(
            coverage["matched"] + coverage["unmatched"],
            coverage["exposure_occupations"],
        )
        self.assertEqual(coverage["matched"], self.results["n_occupations"])
        self.assertGreater(coverage["unmatched"], 0)

        # The direction of the selection is the part that matters.
        self.assertGreater(
            coverage["mean_exposure_unmatched"],
            coverage["mean_exposure_matched"],
        )

        # And it has to reach anyone who only reads the console.
        self.assertIn("unmatched", self.completed.stdout)
        self.assertIn(str(coverage["unmatched"]), self.completed.stdout)

    def test_predicted_automatability_reports_its_own_denominator(self):
        """chance_auto is missing for some occupations, so its column differs.

        Reporting mean exposure and mean predicted automatability side by side
        invites reading them off the same sample. They are not: -1 in the source
        means missing, and the missingness is not evenly spread across wage.
        """
        for quintile in self.results["by_wage_quintile"]:
            self.assertIn("n_predicted_automatability", quintile)
            self.assertLessEqual(quintile["n_predicted_automatability"], quintile["n"])

        covered = sum(q["n_predicted_automatability"] for q in self.results["by_wage_quintile"])
        self.assertLess(covered, self.results["n_occupations"])

    def test_thin_major_groups_are_flagged(self):
        """Group means resting on a handful of occupations are labelled as such."""
        thin = self.results["thin_families"]
        self.assertTrue(thin, "expected at least one major group below the threshold")
        for name, count in thin.items():
            self.assertLess(count, self.results["min_family_n"])
            self.assertIn(name, self.completed.stdout)
        self.assertIn("indicative only", self.completed.stdout)

    def test_analysis_reads_only_the_committed_data_directory(self):
        """No fallback that reconstructs the wage table from a scraped cache.

        The repository's claim is that it regenerates from the files in data/.
        A fallback that globs an agent session directory cannot hold on any
        reader's machine and contradicts the provenance in data/SOURCES.md.
        """
        source = (ROOT / "analysis.py").read_text()
        self.assertNotIn("/sessions/", source)
        self.assertNotIn("glob", source)

    def test_figure_is_regenerated(self):
        figure = self.worktree / "figures" / "ai_exposure_wage.png"
        self.assertTrue(figure.is_file())
        self.assertGreater(figure.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
