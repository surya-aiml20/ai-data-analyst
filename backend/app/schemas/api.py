from typing import Any, Literal
from pydantic import BaseModel, Field


class DatasetSummary(BaseModel):
    dataset_id: str
    name: str
    rows: int
    columns: list[str]
    dtypes: dict[str, str]
    missing_values: dict[str, int]
    preview: list[dict[str, Any]]


class UploadResponse(BaseModel):
    session_id: str
    datasets: list[DatasetSummary]


class QueryRequest(BaseModel):
    session_id: str
    question: str = Field(min_length=2)


class ChartSpec(BaseModel):
    type: Literal["bar", "line", "pie", "scatter"]
    title: str
    x: str
    y: str | None = None
    data: list[dict[str, Any]]


class QueryResponse(BaseModel):
    answer: str
    reasoning: list[str]
    generated_code: str | None = None
    sql: str | None = None
    chart: ChartSpec | None = None
    anomalies: list[dict[str, Any]] = []
    insights: list[str] = []


class DashboardMetric(BaseModel):
    label: str
    value: str
    detail: str | None = None


class DashboardResponse(BaseModel):
    session_id: str
    title: str
    metrics: list[DashboardMetric]
    charts: list[ChartSpec]
    insights: list[str]


class ErrorResponse(BaseModel):
    detail: str
