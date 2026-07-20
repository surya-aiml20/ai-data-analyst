import pandas as pd

from app.services.anomaly import detect_anomalies
from app.services.charts import infer_chart


def test_detect_anomalies_flags_extreme_numeric_value():
    df = pd.DataFrame({"region": ["a", "b", "c", "d"], "revenue": [10, 11, 9, 1000]})

    anomalies = detect_anomalies(df, limit=5)

    assert anomalies
    assert anomalies[0]["column"] == "revenue"


def test_infer_chart_returns_bar_for_top_query():
    df = pd.DataFrame({"region": ["east", "west"], "revenue": [100, 200]})

    chart = infer_chart("show top regions by revenue", df)

    assert chart is not None
    assert chart["type"] == "bar"
    assert chart["x"] == "region"
