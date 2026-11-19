import hashlib
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS experiments (
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
    output_checksum TEXT,
    error_message TEXT,
    reproduction_command TEXT NOT NULL,
    FOREIGN KEY (parent_experiment_id) REFERENCES experiments(id)
);

CREATE TRIGGER IF NOT EXISTS prevent_experiment_update
BEFORE UPDATE ON experiments
BEGIN
    SELECT RAISE(ABORT, 'Historical experiment records are immutable and cannot be modified.');
END;

CREATE TRIGGER IF NOT EXISTS prevent_experiment_delete
BEFORE DELETE ON experiments
BEGIN
    SELECT RAISE(ABORT, 'Historical experiment records are immutable and cannot be deleted.');
END;

CREATE TABLE IF NOT EXISTS literature_sources (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    external_id TEXT NOT NULL,
    title TEXT NOT NULL,
    authors_json TEXT NOT NULL,
    published_date TEXT,
    abstract TEXT,
    access_scope TEXT NOT NULL,
    source_url TEXT NOT NULL,
    license TEXT,
    raw_metadata_json TEXT NOT NULL,
    saved_at TEXT NOT NULL,
    UNIQUE(provider, external_id)
);

CREATE TABLE IF NOT EXISTS hypotheses (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    title TEXT NOT NULL,
    statement TEXT NOT NULL,
    assumptions_json TEXT NOT NULL,
    falsifiable_prediction TEXT NOT NULL,
    test_domain TEXT NOT NULL,
    test_config_json TEXT NOT NULL,
    acceptance_criteria_json TEXT NOT NULL,
    epistemic_status TEXT NOT NULL,
    latest_experiment_id TEXT,
    FOREIGN KEY (latest_experiment_id) REFERENCES experiments(id)
);

CREATE TABLE IF NOT EXISTS verification_runs (
    id TEXT PRIMARY KEY,
    hypothesis_id TEXT NOT NULL,
    experiment_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    passed INTEGER NOT NULL,
    observed_value REAL,
    threshold_description TEXT NOT NULL,
    evaluation_summary TEXT NOT NULL,
    FOREIGN KEY (hypothesis_id) REFERENCES hypotheses(id),
    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
);
CREATE TABLE IF NOT EXISTS datasets (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    row_count INTEGER NOT NULL,
    col_count INTEGER NOT NULL,
    columns_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def compute_checksum(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA_SQL)
            cols = {r["name"] for r in conn.execute("PRAGMA table_info(experiments)").fetchall()}
            if "output_checksum" not in cols:
                conn.execute("ALTER TABLE experiments ADD COLUMN output_checksum TEXT")

    def record_experiment(
        self,
        *,
        domain: str,
        research_question: str,
        methodology: str,
        input_source: str,
        parameters: Dict[str, Any],
        software_versions: Dict[str, str],
        epistemic_label: str,
        status: str,
        output: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        seed: Optional[int] = None,
        parent_experiment_id: Optional[str] = None,
        reproduction_command: str = "",
    ) -> Dict[str, Any]:
        exp_id = f"exp_{uuid.uuid4().hex[:12]}"
        created_at = utc_now_iso()
        checksum = compute_checksum({"domain": domain, "parameters": parameters, "seed": seed})
        output_checksum = compute_checksum(output) if output is not None else None
        if not reproduction_command:
            reproduction_command = f"POST /api/experiments/{exp_id}/rerun"

        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO experiments (
                    id, parent_experiment_id, created_at, domain, research_question,
                    methodology, input_source, input_checksum, parameters_json, seed,
                    software_versions_json, epistemic_label, status, output_json,
                    output_checksum, error_message, reproduction_command
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    exp_id,
                    parent_experiment_id,
                    created_at,
                    domain,
                    research_question,
                    methodology,
                    input_source,
                    checksum,
                    json.dumps(parameters, sort_keys=True),
                    seed,
                    json.dumps(software_versions, sort_keys=True),
                    epistemic_label,
                    status,
                    json.dumps(output, sort_keys=True) if output is not None else None,
                    output_checksum,
                    error_message,
                    reproduction_command,
                ),
            )
        return self.get_experiment(exp_id)  # type: ignore[return-value]

    def _deserialize_experiment(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "parent_experiment_id": row["parent_experiment_id"],
            "created_at": row["created_at"],
            "domain": row["domain"],
            "research_question": row["research_question"],
            "methodology": row["methodology"],
            "input_source": row["input_source"],
            "input_checksum": row["input_checksum"],
            "parameters": json.loads(row["parameters_json"]),
            "seed": row["seed"],
            "software_versions": json.loads(row["software_versions_json"]),
            "epistemic_label": row["epistemic_label"],
            "status": row["status"],
            "output": json.loads(row["output_json"]) if row["output_json"] else None,
            "output_checksum": row["output_checksum"],
            "error_message": row["error_message"],
            "reproduction_command": row["reproduction_command"],
        }

    def get_experiment(self, exp_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM experiments WHERE id = ?", (exp_id,)).fetchone()
            return self._deserialize_experiment(row) if row else None

    def list_experiments(self, limit: int = 50, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            if domain:
                rows = conn.execute(
                    "SELECT * FROM experiments WHERE domain = ? ORDER BY created_at DESC LIMIT ?",
                    (domain, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM experiments ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [self._deserialize_experiment(r) for r in rows]

    def save_literature_source(self, record: Dict[str, Any]) -> Dict[str, Any]:
        rec_id = f"lit_{uuid.uuid4().hex[:12]}"
        saved_at = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO literature_sources (
                    id, provider, external_id, title, authors_json, published_date,
                    abstract, access_scope, source_url, license, raw_metadata_json, saved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(provider, external_id) DO UPDATE SET
                    title = excluded.title,
                    authors_json = excluded.authors_json,
                    published_date = excluded.published_date,
                    abstract = excluded.abstract,
                    access_scope = excluded.access_scope,
                    source_url = excluded.source_url,
                    license = excluded.license,
                    raw_metadata_json = excluded.raw_metadata_json,
                    saved_at = excluded.saved_at
                """,
                (
                    rec_id,
                    record["provider"],
                    record["external_id"],
                    record["title"],
                    json.dumps(record.get("authors", [])),
                    record.get("published_date"),
                    record.get("abstract"),
                    record.get("access_scope", "METADATA_AND_ABSTRACT"),
                    record["source_url"],
                    record.get("license"),
                    json.dumps(record.get("raw_metadata", {})),
                    saved_at,
                ),
            )
            row = conn.execute(
                "SELECT * FROM literature_sources WHERE provider = ? AND external_id = ?",
                (record["provider"], record["external_id"]),
            ).fetchone()
        return self._deserialize_literature(row)

    def _deserialize_literature(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "provider": row["provider"],
            "external_id": row["external_id"],
            "title": row["title"],
            "authors": json.loads(row["authors_json"]),
            "published_date": row["published_date"],
            "abstract": row["abstract"],
            "access_scope": row["access_scope"],
            "source_url": row["source_url"],
            "license": row["license"],
            "saved_at": row["saved_at"],
        }

    def list_literature_sources(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM literature_sources ORDER BY saved_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [self._deserialize_literature(r) for r in rows]

    def create_hypothesis(
        self,
        *,
        title: str,
        statement: str,
        assumptions: List[str],
        falsifiable_prediction: str,
        test_domain: str,
        test_config: Dict[str, Any],
        acceptance_criteria: Dict[str, Any],
    ) -> Dict[str, Any]:
        hyp_id = f"hyp_{uuid.uuid4().hex[:12]}"
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO hypotheses (
                    id, created_at, updated_at, title, statement, assumptions_json,
                    falsifiable_prediction, test_domain, test_config_json,
                    acceptance_criteria_json, epistemic_status, latest_experiment_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
                """,
                (
                    hyp_id,
                    now,
                    now,
                    title,
                    statement,
                    json.dumps(assumptions),
                    falsifiable_prediction,
                    test_domain,
                    json.dumps(test_config, sort_keys=True),
                    json.dumps(acceptance_criteria, sort_keys=True),
                    "PROPOSED_HYPOTHESIS",
                ),
            )
        return self.get_hypothesis(hyp_id)  # type: ignore[return-value]

    def _deserialize_hypothesis(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "title": row["title"],
            "statement": row["statement"],
            "assumptions": json.loads(row["assumptions_json"]),
            "falsifiable_prediction": row["falsifiable_prediction"],
            "test_domain": row["test_domain"],
            "test_config": json.loads(row["test_config_json"]),
            "acceptance_criteria": json.loads(row["acceptance_criteria_json"]),
            "epistemic_status": row["epistemic_status"],
            "latest_experiment_id": row["latest_experiment_id"],
        }

    def get_hypothesis(self, hyp_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM hypotheses WHERE id = ?", (hyp_id,)).fetchone()
            if not row:
                return None
            hyp = self._deserialize_hypothesis(row)
            runs = conn.execute(
                "SELECT * FROM verification_runs WHERE hypothesis_id = ? ORDER BY created_at DESC",
                (hyp_id,),
            ).fetchall()
            hyp["verification_runs"] = [
                {
                    "id": r["id"],
                    "experiment_id": r["experiment_id"],
                    "created_at": r["created_at"],
                    "passed": bool(r["passed"]),
                    "observed_value": r["observed_value"],
                    "threshold_description": r["threshold_description"],
                    "evaluation_summary": r["evaluation_summary"],
                }
                for r in runs
            ]
            return hyp

    def list_hypotheses(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM hypotheses ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [self._deserialize_hypothesis(r) for r in rows]

    def record_verification_run(
        self,
        *,
        hypothesis_id: str,
        experiment_id: str,
        passed: bool,
        observed_value: Optional[float],
        threshold_description: str,
        evaluation_summary: str,
        new_epistemic_status: str,
    ) -> Dict[str, Any]:
        run_id = f"ver_{uuid.uuid4().hex[:12]}"
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO verification_runs (
                    id, hypothesis_id, experiment_id, created_at, passed,
                    observed_value, threshold_description, evaluation_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    hypothesis_id,
                    experiment_id,
                    now,
                    1 if passed else 0,
                    observed_value,
                    threshold_description,
                    evaluation_summary,
                ),
            )
            conn.execute(
                """
                UPDATE hypotheses
                SET epistemic_status = ?, latest_experiment_id = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_epistemic_status, experiment_id, now, hypothesis_id),
            )
        return {
            "id": run_id,
            "hypothesis_id": hypothesis_id,
            "experiment_id": experiment_id,
            "created_at": now,
            "passed": passed,
            "observed_value": observed_value,
            "threshold_description": threshold_description,
            "evaluation_summary": evaluation_summary,
            "epistemic_status": new_epistemic_status,
        }

    def get_counts(self) -> Dict[str, int]:
        with self.connect() as conn:
            return {
                "experiments": conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0],
                "literature_sources": conn.execute("SELECT COUNT(*) FROM literature_sources").fetchone()[0],
                "hypotheses": conn.execute("SELECT COUNT(*) FROM hypotheses").fetchone()[0],
                "verification_runs": conn.execute("SELECT COUNT(*) FROM verification_runs").fetchone()[0],
                "datasets": conn.execute("SELECT COUNT(*) FROM datasets").fetchone()[0],
            }

    def record_dataset(
        self,
        *,
        filename: str,
        checksum_sha256: str,
        row_count: int,
        col_count: int,
        columns: List[str],
    ) -> Dict[str, Any]:
        ds_id = f"ds_{uuid.uuid4().hex[:12]}"
        created_at = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO datasets (id, filename, checksum_sha256, row_count, col_count, columns_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (ds_id, filename, checksum_sha256, row_count, col_count, json.dumps(columns), created_at),
            )
        return {
            "id": ds_id,
            "filename": filename,
            "checksum_sha256": checksum_sha256,
            "row_count": row_count,
            "col_count": col_count,
            "columns": columns,
            "created_at": created_at,
        }

    def list_datasets(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM datasets ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [
                {
                    "id": r["id"],
                    "filename": r["filename"],
                    "checksum_sha256": r["checksum_sha256"],
                    "row_count": r["row_count"],
                    "col_count": r["col_count"],
                    "columns": json.loads(r["columns_json"]),
                    "created_at": r["created_at"],
                }
                for r in rows
            ]
