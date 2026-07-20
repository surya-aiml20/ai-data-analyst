import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type { ChartSpec } from "../types/api";

const colors = ["#0f766e", "#ea580c", "#2563eb", "#9333ea", "#16a34a", "#be123c", "#475569", "#ca8a04"];

export function ChartRenderer({ chart, compact = false }: { chart: ChartSpec; compact?: boolean }) {
  return (
    <div className={`${compact ? "h-72" : "mt-4 h-80"} rounded-md border border-border bg-white p-4`}>
      <h3 className="mb-3 text-sm font-semibold">{chart.title}</h3>
      <ResponsiveContainer width="100%" height="88%">
        {chart.type === "line" ? (
          <LineChart data={chart.data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={chart.x} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey={chart.y ?? ""} stroke="#0f766e" strokeWidth={2} />
          </LineChart>
        ) : chart.type === "pie" ? (
          <PieChart>
            <Pie data={chart.data} dataKey={chart.y ?? ""} nameKey={chart.x} outerRadius={105} label>
              {chart.data.map((_, index) => (
                <Cell key={index} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        ) : chart.type === "scatter" ? (
          <ScatterChart>
            <CartesianGrid />
            <XAxis dataKey={chart.x} name={chart.x} />
            <YAxis dataKey={chart.y ?? ""} name={chart.y ?? ""} />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} />
            <Scatter data={chart.data} fill="#ea580c" />
          </ScatterChart>
        ) : (
          <BarChart data={chart.data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={chart.x} />
            <YAxis />
            <Tooltip />
            <Bar dataKey={chart.y ?? ""} fill="#0f766e" />
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
