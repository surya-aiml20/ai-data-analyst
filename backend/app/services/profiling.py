from __future__ import annotations

import pandas as pd


def numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()


def categorical_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(exclude="number").columns.tolist()


def profile_dataframe(df: pd.DataFrame) -> list[str]:
    insights: list[str] = []
    insights.append(f"Dataset has {len(df):,} rows and {len(df.columns):,} columns.")

    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if not missing.empty:
        top_missing = ", ".join(f"{col} ({count})" for col, count in missing.head(3).items())
        insights.append(f"Missing values are concentrated in: {top_missing}.")
    else:
        insights.append("No missing values were found.")

    for col in numeric_columns(df)[:4]:
        series = df[col].dropna()
        if not series.empty:
            insights.append(
                f"{col} ranges from {series.min():,.2f} to {series.max():,.2f}, "
                f"with an average of {series.mean():,.2f}."
            )

    return insights


def choose_dataset(datasets: dict[str, object]) -> object:
    return next(iter(datasets.values()))
