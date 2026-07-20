from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.api import DashboardResponse, QueryRequest, QueryResponse, UploadResponse
from app.services.analyst import AnalystAgent
from app.services.dashboard import generate_dashboard, generate_markdown_report
from app.services.dataset_store import DatasetStore, summarize_dataset

app = FastAPI(title="AI Data Analyst API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = DatasetStore()
agent = AnalystAgent()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload(files: list[UploadFile] = File(...)) -> UploadResponse:
    try:
        payload = [(file.filename or "upload.csv", await file.read()) for file in files]
        session = store.create_session(payload)
        return UploadResponse(
            session_id=session.session_id,
            datasets=[summarize_dataset(dataset) for dataset in session.datasets.values()],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    try:
        session = store.get_session(request.session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return QueryResponse(**agent.answer(request.question, session))


@app.get("/dashboard/{session_id}", response_model=DashboardResponse)
def dashboard(session_id: str) -> DashboardResponse:
    try:
        session = store.get_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return DashboardResponse(**generate_dashboard(session))


@app.get("/report/{session_id}")
def export_report(session_id: str) -> Response:
    try:
        session = store.get_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    markdown = generate_markdown_report(session)
    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": 'attachment; filename="ai-data-analyst-report.md"'},
    )
