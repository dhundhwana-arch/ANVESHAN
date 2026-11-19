import unittest

from backend.engines.dataset_engine import analyze_csv_dataset


class TestDatasetEngine(unittest.TestCase):
    def test_csv_stats_correlation_and_regression(self):
        csv_bytes = b"x,y\n1,2\n2,4\n3,6\n4,8\n5,10\n"
        res = analyze_csv_dataset(csv_bytes, filename="linear.csv", x_col="x", y_col="y")
        self.assertEqual(res["row_count"], 5)
        self.assertEqual(len(res["checksum_sha256"]), 64)
        self.assertAlmostEqual(res["pearson_correlation_matrix"]["x"]["y"], 1.0, places=6)
        self.assertAlmostEqual(res["linear_regression"]["slope"], 2.0, places=6)
        self.assertAlmostEqual(res["linear_regression"]["r_squared"], 1.0, places=6)
        self.assertIn("causation", res["linear_regression"]["causation_warning"].lower())

    def test_empty_and_invalid_csv_rejected(self):
        with self.assertRaises(ValueError):
            analyze_csv_dataset(b"   ", filename="empty.csv")
        with self.assertRaises(ValueError):
            analyze_csv_dataset(b"a,b\n1,2\n3,4\n", x_col="missing", y_col="b")

    def test_single_row_std_sample_is_none_and_multi_row_uses_ddof_1(self):
        one_row = analyze_csv_dataset(b"x,y\n10,20\n", filename="one.csv")
        self.assertIsNone(one_row["numeric_summary"]["x"]["std_sample"])
        self.assertIsNone(one_row["numeric_summary"]["y"]["std_sample"])

        two_rows = analyze_csv_dataset(b"x\n2\n4\n", filename="two.csv")
        # ddof=1 sample std of [2, 4] is sqrt(2) = 1.4142135623730951
        self.assertAlmostEqual(two_rows["numeric_summary"]["x"]["std_sample"], 2.0 ** 0.5, places=9)
