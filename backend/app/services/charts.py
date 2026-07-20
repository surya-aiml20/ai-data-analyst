from __future__ import annotations

import pandas as pd


def infer_chart(question: str, df: pd.DataFrame) -> dict[str, object] | None:
    q = question.lower()
    numeric = df.select_dtypes(include="number").columns.tolist()
    non_numeric = df.select_dtypes(exclude="number").columns.tolist()
    date_like = [col for col in df.columns if "date" in col or "month" in col or "time" in col]

    if not numeric:
        return None

    y = _prefer_metric(numeric)
    if any(word in q for word in ["trend", "monthly", "over time", "line"]):
        x = date_like[0] if date_like else df.columns[0]
        data = df.groupby(x, dropna=False)[y].sum().reset_index().sort_values(x).to_dict("records")
        return {"type": "line", "title": f"{y} over {x}", "x": x, "y": y, "data": data}

    if "scatter" in q and len(numeric) >= 2:
        return {
            "type": "scatter",
            "title": f"{numeric[1]} vs {numeric[0]}",
            "x": numeric[0],
            "y": numeric[1],
            "data": df[[numeric[0], numeric[1]]].dropna().head(200).to_dict("records"),
        }

    if "pie" in q and non_numeric:
        x = _prefer_dimension(non_numeric)
        data = df.groupby(x, dropna=False)[y].sum().nlargest(8).reset_index().to_dict("records")
        return {"type": "pie", "title": f"{y} share by {x}", "x": x, "y": y, "data": data}

    if any(word in q for word in ["chart", "show", "plot", "bar", "top", "highest"]) and non_numeric:
        x = _prefer_dimension(non_numeric)
        data = df.groupby(x, dropna=False)[y].sum().nlargest(10).reset_index().to_dict("records")
        return {"type": "bar", "title": f"Top {x} by {y}", "x": x, "y": y, "data": data}

    return None


def _prefer_metric(columns: list[str]) -> str:
    for preferred in ["revenue", "sales", "profit", "amount", "total"]:
        for col in columns:
            if preferred in col:
                return col
    return columns[0]


def _prefer_dimension(columns: list[str]) -> str:
    for preferred in ["region", "product", "customer", "category", "segment"]:
        for col in columns:
            if preferred in col:
                return col
    return columns[0]
