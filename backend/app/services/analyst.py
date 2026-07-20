from __future__ import annotations

import re
from typing import Any

import pandas as pd

from app.config import get_settings
from app.services.anomaly import detect_anomalies
from app.services.charts import infer_chart
from app.services.profiling import profile_dataframe


class AnalystAgent:
    def answer(self, question: str, session: Any) -> dict[str, Any]:
        dataset = next(iter(session.datasets.values()))
        df = session.analysis_frame()
        session.messages.append({"role": "user", "content": question})

        deterministic = self._deterministic_answer(question, df)
        anomalies = detect_anomalies(df) if "anomal" in question.lower() else []
        chart = infer_chart(question, df)
        insights = profile_dataframe(df) if any(w in question.lower() for w in ["insight", "summary", "summarize"]) else []

        response = {
            "answer": deterministic["answer"],
            "reasoning": deterministic["reasoning"],
            "generated_code": deterministic.get("generated_code"),
            "sql": deterministic.get("sql"),
            "chart": chart,
            "anomalies": anomalies,
            "insights": insights,
        }

        settings = get_settings()
        if settings.groq_api_key:
            dataset_names = ", ".join(dataset.name for dataset in session.datasets.values())
            response["answer"] = self._llm_polish(question, dataset_names, response)

        session.messages.append({"role": "assistant", "content": response["answer"]})
        return response

    def _deterministic_answer(self, question: str, df: pd.DataFrame) -> dict[str, Any]:
        q = question.lower()
        numeric = df.select_dtypes(include="number").columns.tolist()
        dimensions = df.select_dtypes(exclude="number").columns.tolist()
        metric = self._metric_for(q, numeric)
        dimension = self._dimension_for(q, dimensions)

        if "sql" in q:
            sql = self._sql_for(q, metric, dimension)
            return {
                "answer": "Here is DuckDB-compatible SQL for the analysis.",
                "reasoning": ["Identified the requested metric and grouping fields.", "Generated SQL against the uploaded table."],
                "sql": sql,
                "generated_code": f"duckdb.sql({sql!r}).df()",
            }

        if "anomal" in q:
            return {
                "answer": "I scanned numeric columns for high z-score outliers and listed rows with unusually distant values.",
                "reasoning": ["Selected numeric columns.", "Computed standardized distance from each column mean.", "Flagged rows above the anomaly threshold."],
                "generated_code": "zscores = (numeric - numeric.mean()) / numeric.std(ddof=0); zscores.abs().max(axis=1) >= 2.5",
            }

        if metric and dimension and any(w in q for w in ["highest", "top", "best", "five", "5"]):
            grouped = df.groupby(dimension, dropna=False)[metric].sum().sort_values(ascending=False)
            top_n = 5 if re.search(r"\b(five|5)\b", q) else 1
            result = grouped.head(top_n)
            label = ", ".join(f"{idx}: {value:,.2f}" for idx, value in result.items())
            return {
                "answer": f"Top result by {metric}: {label}.",
                "reasoning": [f"Grouped rows by {dimension}.", f"Summed {metric} for each group.", "Sorted groups from highest to lowest."],
                "generated_code": f"df.groupby('{dimension}')['{metric}'].sum().sort_values(ascending=False).head({top_n})",
            }

        if metric and dimension and any(w in q for w in ["underperform", "lowest", "bottom"]):
            grouped = df.groupby(dimension, dropna=False)[metric].sum().sort_values()
            result = grouped.head(5)
            label = ", ".join(f"{idx}: {value:,.2f}" for idx, value in result.items())
            return {
                "answer": f"Lowest performers by {metric}: {label}.",
                "reasoning": [f"Grouped rows by {dimension}.", f"Summed {metric}.", "Sorted ascending to identify underperformance."],
                "generated_code": f"df.groupby('{dimension}')['{metric}'].sum().sort_values().head(5)",
            }

        if any(w in q for w in ["trend", "monthly"]) and metric:
            date_col = next((col for col in df.columns if "month" in col or "date" in col), df.columns[0])
            grouped = df.groupby(date_col, dropna=False)[metric].sum().sort_index()
            latest = grouped.tail(3)
            label = ", ".join(f"{idx}: {value:,.2f}" for idx, value in latest.items())
            return {
                "answer": f"Recent {metric} trend points are {label}. See the generated line chart for the full pattern.",
                "reasoning": [f"Used {date_col} as the time axis.", f"Aggregated {metric} by time period.", "Prepared a trend chart."],
                "generated_code": f"df.groupby('{date_col}')['{metric}'].sum().sort_index()",
            }

        return {
            "answer": "I profiled the uploaded data and prepared a concise summary. Ask for a chart, top customers, anomalies, SQL, or a dashboard to drill deeper.",
            "reasoning": ["Loaded the combined analysis frame.", "Inspected column types and missing values.", "Prepared reusable metrics for follow-up questions."],
            "generated_code": "df.describe(include='all')",
        }

    def _metric_for(self, question: str, numeric: list[str]) -> str | None:
        if not numeric:
            return None
        for token in ["revenue", "sales", "profit", "amount", "quantity", "total"]:
            for col in numeric:
                if token in question and token in col:
                    return col
        return next((col for col in numeric if "revenue" in col or "sales" in col), numeric[0])

    def _dimension_for(self, question: str, dimensions: list[str]) -> str | None:
        if not dimensions:
            return None
        for col in dimensions:
            if col in question:
                return col
        for token in ["region", "product", "customer", "category"]:
            for col in dimensions:
                if token in question and token in col:
                    return col
        return dimensions[0]

    def _sql_for(self, question: str, metric: str | None, dimension: str | None) -> str:
        if metric and dimension:
            return f"SELECT {dimension}, SUM({metric}) AS total_{metric} FROM uploaded_data GROUP BY {dimension} ORDER BY total_{metric} DESC LIMIT 5;"
        return "SELECT * FROM uploaded_data LIMIT 10;"

    def _llm_polish(self, question: str, dataset_name: str, response: dict[str, Any]) -> str:
        try:
            from langchain_groq import ChatGroq
            from langchain_core.messages import HumanMessage, SystemMessage

            llm = ChatGroq(api_key=get_settings().groq_api_key, model=get_settings().groq_model, temperature=0.1)
            messages = [
                SystemMessage(content="You are a careful data analyst. Explain results succinctly and cite the computation steps."),
                HumanMessage(content=f"Dataset: {dataset_name}\nQuestion: {question}\nComputed result: {response}"),
            ]
            return llm.invoke(messages).content
        except Exception:
            return response["answer"]
