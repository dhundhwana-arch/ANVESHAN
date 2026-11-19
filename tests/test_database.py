import sqlite3
import tempfile
import unittest
from pathlib import Path

from backend.database import Database


class TestDatabaseIntegrity(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmpdir.name) / "test_anveshan.db")
        self.db = Database(self.db_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_experiment_immutability_triggers(self):
        exp = self.db.record_experiment(
            domain="math_symbolic",
            research_question="Test immutability",
            methodology="Unit test",
            input_source="test",
            parameters={"x": 1},
            software_versions={"python": "3.11"},
            epistemic_label="COMPUTATIONAL_RESULT",
            status="COMPLETED",
            output={"y": 2},
        )
        self.assertIsNotNone(exp["input_checksum"])
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.connect() as conn:
                conn.execute("UPDATE experiments SET status = 'TAMPERED' WHERE id = ?", (exp["id"],))
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.connect() as conn:
                conn.execute("DELETE FROM experiments WHERE id = ?", (exp["id"],))

    def test_literature_upsert_and_counts(self):
        rec = {
            "provider": "arxiv",
            "external_id": "2401.00001",
            "title": "Sample Fixture Paper",
            "authors": ["A. Researcher"],
            "published_date": "2024-01-01",
            "abstract": "Fixture abstract.",
            "access_scope": "METADATA_AND_ABSTRACT",
            "source_url": "https://arxiv.org/abs/2401.00001",
            "license": "arXiv",
        }
        saved1 = self.db.save_literature_source(rec)
        saved2 = self.db.save_literature_source(rec)
        self.assertEqual(saved1["external_id"], saved2["external_id"])
        self.assertEqual(self.db.get_counts()["literature_sources"], 1)

    def test_backward_compatible_output_checksum_migration_preserves_legacy_rows(self):
        legacy_path = str(Path(self.tmpdir.name) / "legacy_v1_0.db")
        # Create a legacy experiments table WITHOUT output_checksum
        conn = sqlite3.connect(legacy_path)
        conn.executescript('''
            CREATE TABLE experiments (
                id TEXT PRIMARY KEY,
                parent_experiment_id TEXT,
                created_at TEXT NOT NULL,
                domain TEXT NOT NULL,
                research_question TEXT NOT NULL,
                methodology TEXT NOT NULL,
                input_source TEXT NOT NULL,
                input_checksum TEXT NOT NULL,
                parameters_json TEXT NOT NULL,
                seed INTEGER,
                software_versions_json TEXT NOT NULL,
                epistemic_label TEXT NOT NULL,
                status TEXT NOT NULL,
                output_json TEXT,
                error_message TEXT,
                reproduction_command TEXT NOT NULL
            );
            INSERT INTO experiments VALUES (
                'exp_legacy001', NULL, '2026-11-18T00:00:00Z', 'math_symbolic',
                'Legacy run', 'SymPy', 'user', 'abc123', '{}', NULL, '{}',
                'COMPUTATIONAL_RESULT', 'COMPLETED', '{"v": 1}', NULL, 'POST /rerun'
            );
        ''')
        conn.commit()
        conn.close()

        # Opening Database should safely migrate without altering legacy row
        migrated_db = Database(legacy_path)
        legacy_rec = migrated_db.get_experiment("exp_legacy001")
        self.assertIsNotNone(legacy_rec)
        self.assertIsNone(legacy_rec["output_checksum"])

        # New experiment gets deterministic 64-char output_checksum
        new_rec = migrated_db.record_experiment(
            domain="math_symbolic",
            research_question="Post-migration run",
            methodology="Unit test",
            input_source="test",
            parameters={"x": 2},
            software_versions={"anveshan": "1.2.0"},
            epistemic_label="COMPUTATIONAL_RESULT",
            status="COMPLETED",
            output={"result": 4},
        )
        self.assertEqual(len(new_rec["output_checksum"]), 64)
