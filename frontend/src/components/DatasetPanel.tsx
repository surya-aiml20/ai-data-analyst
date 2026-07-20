import type { DatasetSummary } from "../types/api";
import { Button } from "./Button";

type Props = {
  datasets: DatasetSummary[];
  onGenerateDashboard: () => void;
  onExportReport: () => void;
  busy: boolean;
};

export function DatasetPanel({ datasets, onGenerateDashboard, onExportReport, busy }: Props) {
  return (
    <aside className="min-h-0 border-r border-border bg-white">
      <div className="border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Datasets</h2>
      </div>
      <div className="grid gap-2 border-b border-border p-4">
        <Button variant="secondary" disabled={!datasets.length || busy} onClick={onGenerateDashboard}>
          Generate dashboard
        </Button>
        <Button variant="secondary" disabled={!datasets.length || busy} onClick={onExportReport}>
          Export report
        </Button>
      </div>
      <div className="space-y-4 p-4">
        {datasets.map((dataset) => (
          <article key={dataset.dataset_id} className="rounded-md border border-border bg-background p-3">
            <div className="flex items-start justify-between gap-3">
              <h3 className="font-semibold">{dataset.name}</h3>
              <span className="rounded bg-white px-2 py-1 text-xs text-slate-600">{dataset.rows} rows</span>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {dataset.columns.map((column) => (
                <span key={column} className="rounded border border-border bg-white px-2 py-1 text-xs text-slate-700">
                  {column}
                </span>
              ))}
            </div>
          </article>
        ))}
      </div>
    </aside>
  );
}
