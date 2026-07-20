import { BarChart3 } from "lucide-react";
import type { DashboardResponse } from "../types/api";
import { ChartRenderer } from "./ChartRenderer";

type Props = {
  dashboard: DashboardResponse | null;
};

export function DashboardPanel({ dashboard }: Props) {
  if (!dashboard) {
    return null;
  }

  return (
    <section className="border-b border-border bg-white">
      <div className="mx-auto max-w-7xl px-5 py-5">
        <div className="mb-4 flex items-center gap-2">
          <BarChart3 size={18} className="text-primary" />
          <h2 className="text-base font-semibold">{dashboard.title}</h2>
        </div>
        <div className="grid gap-3 md:grid-cols-4">
          {dashboard.metrics.map((metric) => (
            <article key={metric.label} className="rounded-md border border-border bg-background p-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{metric.label}</p>
              <p className="mt-1 text-2xl font-semibold">{metric.value}</p>
              {metric.detail && <p className="mt-1 text-xs text-slate-600">{metric.detail}</p>}
            </article>
          ))}
        </div>
        <div className="mt-4 grid gap-4 xl:grid-cols-2">
          {dashboard.charts.map((chart) => (
            <ChartRenderer key={`${chart.type}-${chart.title}-${chart.x}-${chart.y}`} chart={chart} compact />
          ))}
        </div>
        <div className="mt-4 rounded-md border border-border bg-background p-3">
          <h3 className="text-sm font-semibold">Dashboard insights</h3>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
            {dashboard.insights.map((insight) => (
              <li key={insight}>{insight}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
