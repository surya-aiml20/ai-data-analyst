from __future__ import annotations

import io
import uuid
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class Dataset:
    dataset_id: str
    name: str
    frame: pd.DataFrame


@dataclass
class AnalysisSession:
    session_id: str
    datasets: dict[str, Dataset] = field(default_factory=dict)
    messages: list[dict[str, str]] = field(default_factory=list)

    def analysis_frame(self) -> pd.DataFrame:
        datasets = list(self.datasets.values())
        if not datasets:
            return pd.DataFrame()
        if len(datasets) == 1:
            return datasets[0].frame.copy()

        merged = datasets[0].frame.copy()
        used_merge = False
        for dataset in datasets[1:]:
            common = [col for col in merged.columns if col in dataset.frame.columns]
            if common:
                merged = merged.merge(dataset.frame, on=common, how="left", suffixes=("", f"_{dataset.dataset_id[:8]}"))
                used_merge = True

        if used_merge:
            merged.insert(0, "__analysis_source", "multi_file_join")
            return merged

        frames = []
        for dataset in datasets:
            frame = dataset.frame.copy()
            frame.insert(0, "__dataset", dataset.name)
            frames.append(frame)
        return pd.concat(frames, ignore_index=True, sort=False)


class DatasetStore:
    def __init__(self) -> None:
        self._sessions: dict[str, AnalysisSession] = {}

    def create_session(self, files: list[tuple[str, bytes]]) -> AnalysisSession:
        if not files:
            raise ValueError("Upload at least one CSV file.")

        session = AnalysisSession(session_id=str(uuid.uuid4()))
        for filename, content in files:
            dataset = self._parse_csv(filename, content)
            session.datasets[dataset.dataset_id] = dataset

        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> AnalysisSession:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise KeyError("Session not found. Upload CSV files first.") from exc

    def _parse_csv(self, filename: str, content: bytes) -> Dataset:
        if not filename.lower().endswith(".csv"):
            raise ValueError(f"{filename} is not a CSV file.")
        if not content:
            raise ValueError(f"{filename} is empty.")

        try:
            df = pd.read_csv(io.BytesIO(content))
        except Exception as exc:
            raise ValueError(f"Could not parse {filename}: {exc}") from exc

        if df.empty:
            raise ValueError(f"{filename} contains no rows.")
        if df.columns.duplicated().any():
            duplicated = df.columns[df.columns.duplicated()].tolist()
            raise ValueError(f"{filename} has duplicate columns: {duplicated}")

        df.columns = [str(col).strip().replace(" ", "_").lower() for col in df.columns]
        return Dataset(dataset_id=str(uuid.uuid4()), name=filename, frame=df)


def summarize_dataset(dataset: Dataset, preview_rows: int = 10) -> dict[str, Any]:
    df = dataset.frame
    return {
        "dataset_id": dataset.dataset_id,
        "name": dataset.name,
        "rows": len(df),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": df.isna().sum().astype(int).to_dict(),
        "preview": df.head(preview_rows).where(pd.notna(df), None).to_dict(orient="records"),
    }
