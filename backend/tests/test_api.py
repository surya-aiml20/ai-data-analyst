from fastapi.testclient import TestClient

from app.main import app


def test_upload_and_query_sales_csv():
    client = TestClient(app)
    csv = b"region,revenue\nNorth,100\nSouth,200\n"

    upload = client.post("/upload", files=[("files", ("sales.csv", csv, "text/csv"))])
    assert upload.status_code == 200
    session_id = upload.json()["session_id"]

    query = client.post("/query", json={"session_id": session_id, "question": "Which region generated the highest revenue?"})
    assert query.status_code == 200
    body = query.json()
    assert "South" in body["answer"]
    assert body["generated_code"]


def test_dashboard_and_report_support_multiple_files():
    client = TestClient(app)
    sales = b"customer,region,revenue\nAcme,North,100\nGlobex,South,200\n"
    customers = b"customer,industry,tier\nAcme,Manufacturing,Enterprise\nGlobex,Retail,Mid-Market\n"

    upload = client.post(
        "/upload",
        files=[
            ("files", ("sales.csv", sales, "text/csv")),
            ("files", ("customers.csv", customers, "text/csv")),
        ],
    )
    assert upload.status_code == 200
    session_id = upload.json()["session_id"]

    dashboard = client.get(f"/dashboard/{session_id}")
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["metrics"][0]["value"] == "2"
    assert body["charts"]

    report = client.get(f"/report/{session_id}")
    assert report.status_code == 200
    assert "AI Data Analyst Report" in report.text
    assert "sales.csv" in report.text
