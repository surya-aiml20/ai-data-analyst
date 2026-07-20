export type DatasetSummary = {
  dataset_id: string;
  name: string;
  rows: number;
  columns: string[];
  dtypes: Record<string, string>;
  missing_values: Record<string, number>;
  preview: Record<string, unknown>[];
};

export type ChartSpec = {
  type: "bar" | "line" | "pie" | "scatter";
  title: string;
  x: string;
  y?: string | null;
  data: Record<string, string | number | null>[];
};

export type QueryResponse = {
  answer: string;
  reasoning: string[];
  generated_code?: string | null;
  sql?: string | null;
  chart?: ChartSpec | null;
  anomalies: Record<string, unknown>[];
  insights: string[];
};

export type DashboardMetric = {
  label: string;
  value: string;
  detail?: string | null;
};

export type DashboardResponse = {
  session_id: string;
  title: string;
  metrics: DashboardMetric[];
  charts: ChartSpec[];
  insights: string[];
};

export type UploadResponse = {
  session_id: string;
  datasets: DatasetSummary[];
};
