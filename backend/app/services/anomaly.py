from __future__ import annotations

import pandas as pd


def detect_anomalies(df: pd.DataFrame, limit: int = 10) -> list[dict[str, object]]:
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        return []

    if len(numeric) >= 8:
        sklearn_rows = _isolation_forest_anomalies(df, numeric, limit)
        if sklearn_rows:
            return sklearn_rows

    return _zscore_anomalies(df, numeric, limit)


def _zscore_anomalies(df: pd.DataFrame, numeric: pd.DataFrame, limit: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    zscores = (numeric - numeric.mean()) / numeric.std(ddof=0).replace(0, 1)
    threshold = 1.5 if len(numeric) < 8 else 2.5
    mask = zscores.abs().max(axis=1) >= threshold

    for idx in numeric[mask].index[:limit]:
        strongest_col = zscores.loc[idx].abs().idxmax()
        rows.append(
            {
                "row_index": int(idx),
                "column": str(strongest_col),
                "value": float(df.loc[idx, strongest_col]),
                "score": round(float(zscores.loc[idx, strongest_col]), 2),
                "reason": f"{strongest_col} is unusually far from the column average.",
                "row": df.loc[idx].where(pd.notna(df.loc[idx]), None).to_dict(),
            }
        )
    return rows


def _isolation_forest_anomalies(df: pd.DataFrame, numeric: pd.DataFrame, limit: int) -> list[dict[str, object]]:
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler
    except Exception:
        return []

    clean = numeric.fillna(numeric.median(numeric_only=True))
    scaled = StandardScaler().fit_transform(clean)
    contamination = min(0.2, max(0.05, 1 / len(clean)))
    model = IsolationForest(contamination=contamination, random_state=42)
    labels = model.fit_predict(scaled)
    scores = model.decision_function(scaled)
    flagged = clean.index[labels == -1]

    rows: list[dict[str, object]] = []
    for idx in flagged[:limit]:
        strongest_col = (numeric.loc[idx] - numeric.mean()).abs().idxmax()
        rows.append(
            {
                "row_index": int(idx),
                "column": str(strongest_col),
                "value": float(df.loc[idx, strongest_col]),
                "score": round(float(scores[list(clean.index).index(idx)]), 4),
                "reason": f"Isolation Forest marked this row as unusual; {strongest_col} contributed the largest numeric deviation.",
                "row": df.loc[idx].where(pd.notna(df.loc[idx]), None).to_dict(),
            }
        )
    return rows
