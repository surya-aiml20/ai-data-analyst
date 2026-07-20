import { UploadCloud } from "lucide-react";
import { useDropzone } from "react-dropzone";
import { Button } from "./Button";

type Props = {
  onUpload: (files: File[]) => void;
  loading: boolean;
};

export function FileUploader({ onUpload, loading }: Props) {
  const { getRootProps, getInputProps, acceptedFiles } = useDropzone({
    accept: { "text/csv": [".csv"] },
    multiple: true
  });

  return (
    <section className="border-b border-border bg-white">
      <div className="mx-auto grid max-w-7xl gap-4 px-5 py-5 md:grid-cols-[1fr_auto] md:items-center">
        <div
          {...getRootProps()}
          className="flex min-h-28 cursor-pointer items-center gap-4 rounded-md border border-dashed border-slate-300 bg-background px-5 py-4 hover:border-primary"
        >
          <input {...getInputProps()} />
          <div className="flex h-11 w-11 items-center justify-center rounded-md bg-teal-50 text-primary">
            <UploadCloud size={22} aria-hidden />
          </div>
          <div>
            <h1 className="text-xl font-semibold">AI Data Analyst</h1>
            <p className="mt-1 text-sm text-slate-600">
              Drop one or more CSV files, then ask for insights, SQL, anomalies, and charts.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3 md:justify-end">
          <span className="max-w-64 truncate text-sm text-slate-600">
            {acceptedFiles.length ? acceptedFiles.map((file) => file.name).join(", ") : "No files selected"}
          </span>
          <Button onClick={() => onUpload(Array.from(acceptedFiles))} disabled={!acceptedFiles.length || loading}>
            {loading ? "Uploading" : "Analyze"}
          </Button>
        </div>
      </div>
    </section>
  );
}
