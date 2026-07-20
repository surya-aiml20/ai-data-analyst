from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.charts import infer_chart
from app.services.profiling import profile_dataframe


def generate_dashboard(session: Any) -> dict[str, Any]:
    df = session.analysis_frame()
    charts = []
    for question in [
        "show top categories by revenue as a bar chart",
        "show monthly sales trends",
        "show revenue share as a pie chart",
        "show scatter relationship between numeric columns",
    ]:
        chart = infer_chart(question, df)
        if chart and _chart_signature(chart) not in {_chart_signature(existing) for existing in charts}:
            charts.append(chart)

    metrics = _metrics(session, df)
    insights = _multi_file_insights(session, df) + profile_dataframe(df)[:4]
    return {
        "session_id": session.session_id,
        "title": "Generated dashboard",
        "metrics": metrics,
        "charts": charts[:4],
        "insights": insights,
    }


def generate_markdown_report(session: Any) -> str:
    dashboard = generate_dashboard(session)
    lines = [
        "# AI Data Analyst Report",
        "",
        "## Uploaded Datasets",
    ]
    for dataset in session.datasets.values():
        lines.append(f"- {dataset.name}: {len(dataset.frame):,} rows, {len(dataset.frame.columns):,} columns")

    lines.extend(["", "## Key Metrics"])
    for metric in dashboard["metrics"]:
        detail = f" - {metric['detail']}" if metric.get("detail") else ""
        lines.append(f"- {metric['label']}: {metric['value']}{detail}")

    lines.extend(["", "## Insights"])
    for insight in dashboard["insights"]:
        lines.append(f"- {insight}")

    if session.messages:
        lines.extend(["", "## Conversation Summary"])
        for message in session.messages[-8:]:
            role = message["role"].title()
            lines.append(f"- **{role}:** {message['content']}")

    lines.extend(["", "## Generated Charts"])
    for chart in dashboard["charts"]:
        lines.append(f"- {chart['title']} ({chart['type']})")

    return "\n".join(lines) + "\n"


def _metrics(session: Any, df: pd.DataFrame) -> list[dict[str, str]]:
    numeric = df.select_dtypes(include="number")
    metrics = [
        {"label": "Datasets", "value": str(len(session.datasets)), "detail": "Uploaded CSV files in this session"},
        {"label": "Analysis rows", "value": f"{len(df):,}", "detail": "Rows in the combined analysis frame"},
        {"label": "Analysis columns", "value": f"{len(df.columns):,}", "detail": "Columns available after multi-file alignment"},
    ]
    if not numeric.empty:
        metric_col = next((col for col in numeric.columns if "revenue" in col or "sales" in col), numeric.columns[0])
        metrics.append({"label": f"Total {metric_col}", "value": f"{numeric[metric_col].sum():,.2f}", "detail": "Summed across the analysis frame"})
    return metrics


def _multi_file_insights(session: Any, df: pd.DataFrame) -> list[str]:
    if len(session.datasets) == 1:
        return ["Dashboard is based on one uploaded dataset."]
    common_columns = set.intersection(*(set(dataset.frame.columns) for dataset in session.datasets.values()))
    if common_columns:
        columns = ", ".join(sorted(common_columns))
        return [f"Multi-file analysis joined datasets using shared columns: {columns}."]
    return ["Multi-file analysis stacked datasets because no shared join columns were found."]


def _chart_signature(chart: dict[str, Any]) -> tuple[str, str, str | None]:
    return (str(chart.get("type")), str(chart.get("x")), chart.get("y"))
