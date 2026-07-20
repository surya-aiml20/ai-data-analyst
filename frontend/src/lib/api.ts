import type { DashboardResponse, QueryResponse, UploadResponse } from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function uploadCsvFiles(files: File[]): Promise<UploadResponse> {
  const form = new FormData();
  files.forEach((file) => form.append("files", file));

  const response = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: form
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return response.json();
}

export async function askQuestion(sessionId: string, question: string): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, question })
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return response.json();
}

export async function generateDashboard(sessionId: string): Promise<DashboardResponse> {
  const response = await fetch(`${API_BASE}/dashboard/${sessionId}`);

  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return response.json();
}

export async function exportReport(sessionId: string): Promise<Blob> {
  const response = await fetch(`${API_BASE}/report/${sessionId}`);

  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return response.blob();
}

async function readError(response: Response): Promise<string> {
  try {
    const payload = await response.json();
    return payload.detail ?? "Request failed";
  } catch {
    return "Request failed";
  }
}
