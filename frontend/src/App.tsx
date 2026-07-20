import { useState } from "react";
import { ChatPanel } from "./components/ChatPanel";
import { DashboardPanel } from "./components/DashboardPanel";
import { DatasetPanel } from "./components/DatasetPanel";
import { FileUploader } from "./components/FileUploader";
import { askQuestion, exportReport, generateDashboard, uploadCsvFiles } from "./lib/api";
import type { DashboardResponse, DatasetSummary, QueryResponse } from "./types/api";

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [busy, setBusy] = useState(false);

  async function handleUpload(files: File[]) {
    setUploading(true);
    setError(null);
    try {
      const response = await uploadCsvFiles(files);
      setSessionId(response.session_id);
      setDatasets(response.datasets);
      setDashboard(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function handleAsk(question: string): Promise<QueryResponse> {
    if (!sessionId) throw new Error("Upload CSV files first.");
    setError(null);
    try {
      return await askQuestion(sessionId, question);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Query failed";
      setError(message);
      throw err;
    }
  }

  async function handleGenerateDashboard() {
    if (!sessionId) return;
    setBusy(true);
    setError(null);
    try {
      setDashboard(await generateDashboard(sessionId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Dashboard generation failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleExportReport() {
    if (!sessionId) return;
    setBusy(true);
    setError(null);
    try {
      const report = await exportReport(sessionId);
      const url = URL.createObjectURL(report);
      const link = document.createElement("a");
      link.href = url;
      link.download = "ai-data-analyst-report.md";
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Report export failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex h-screen flex-col bg-background text-foreground">
      <FileUploader onUpload={handleUpload} loading={uploading} />
      {error && <div className="border-b border-red-200 bg-red-50 px-5 py-2 text-sm text-red-700">{error}</div>}
      <DashboardPanel dashboard={dashboard} />
      <div className="grid min-h-0 flex-1 md:grid-cols-[340px_1fr]">
        <DatasetPanel
          datasets={datasets}
          busy={busy}
          onGenerateDashboard={handleGenerateDashboard}
          onExportReport={handleExportReport}
        />
        <ChatPanel disabled={!sessionId} onAsk={handleAsk} />
      </div>
    </div>
  );
}
