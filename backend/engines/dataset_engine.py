import hashlib
import io
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from scipy import stats


MAX_CSV_BYTES = 2 * 1024 * 1024  # 2 MB safety limit


def analyze_csv_dataset(
    csv_bytes: bytes,
    filename: str = "uploaded.csv",
    x_col: Optional[str] = None,
    y_col: Optional[str] = None,
) -> Dict[str, Any]:
    if not csv_bytes or not csv_bytes.strip():
        raise ValueError("CSV payload is empty.")
    if len(csv_bytes) > MAX_CSV_BYTES:
        raise ValueError(f"CSV file exceeds maximum size limit ({MAX_CSV_BYTES // (1024 * 1024)} MB).")

    checksum = hashlib.sha256(csv_bytes).hexdigest()
    try:
        df = pd.read_csv(io.BytesIO(csv_bytes))
    except Exception as exc:
        raise ValueError(f"Failed to parse CSV file: {exc}") from exc

    if df.empty or len(df.columns) == 0:
        raise ValueError("CSV contains no data rows or columns.")

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    summary: Dict[str, Any] = {}
    for col in numeric_cols:
        series = df[col].dropna().astype(float)
        if series.empty:
            continue
        q25, q50, q75 = np.percentile(series.to_numpy(), [25, 50, 75])
        summary[str(col)] = {
            "count": int(series.size),
            "missing": int(df[col].isna().sum()),
            "mean": float(series.mean()),
            "median": float(q50),
            "std_sample": float(series.std(ddof=1)) if series.size >= 2 else None,
            "min": float(series.min()),
            "max": float(series.max()),
            "q25": float(q25),
            "q75": float(q75),
        }

    corr_matrix: Dict[str, Dict[str, Optional[float]]] = {}
    if len(numeric_cols) >= 2:
        corr_df = df[numeric_cols].corr(method="pearson")
        for r_col in numeric_cols:
            corr_matrix[str(r_col)] = {
                str(c_col): (None if pd.isna(corr_df.loc[r_col, c_col]) else round(float(corr_df.loc[r_col, c_col]), 6))
                for c_col in numeric_cols
            }

    regression: Optional[Dict[str, Any]] = None
    if x_col and y_col:
        if x_col not in df.columns or y_col not in df.columns:
            raise ValueError(f"Requested regression columns '{x_col}', '{y_col}' not found in CSV.")
        if x_col not in numeric_cols or y_col not in numeric_cols:
            raise ValueError("Regression columns must be numeric.")
        paired = df[[x_col, y_col]].dropna().astype(float)
        if len(paired) < 2:
            raise ValueError("At least 2 non-null paired rows are required for regression.")
        xv = paired[x_col].to_numpy()
        yv = paired[y_col].to_numpy()
        if float(np.ptp(xv)) == 0.0:
            raise ValueError(f"Column '{x_col}' has zero variance; cannot fit linear regression.")
        lin = stats.linregress(xv, yv)
        y_pred = lin.slope * xv + lin.intercept
        regression = {
            "x_col": x_col,
            "y_col": y_col,
            "n_paired": int(len(paired)),
            "slope": float(lin.slope),
            "intercept": float(lin.intercept),
            "r_value": float(lin.rvalue),
            "r_squared": float(lin.rvalue ** 2),
            "p_value": float(lin.pvalue),
            "std_err": float(lin.stderr),
            "scatter_points": [
                {"x": float(a), "y": float(b), "y_pred": float(p)}
                for a, b, p in zip(xv[:200], yv[:200], y_pred[:200])
            ],
            "causation_warning": "Observed correlation in tabular data does NOT establish causation.",
        }

    return {
        "filename": filename,
        "checksum_sha256": checksum,
        "row_count": int(len(df)),
        "col_count": int(len(df.columns)),
        "columns": [str(c) for c in df.columns],
        "numeric_columns": [str(c) for c in numeric_cols],
        "missing_by_column": {str(c): int(df[c].isna().sum()) for c in df.columns},
        "numeric_summary": summary,
        "pearson_correlation_matrix": corr_matrix,
        "linear_regression": regression,
    }
