import type { JobStatus } from "../App";

type PreviewPanelProps = {
  previewUrl: string;
  resultUrl: string;
  jobStatus: JobStatus;
  errorMessage: string;
  jobId: string;
};

export default function PreviewPanel({
  previewUrl,
  resultUrl,
  jobStatus,
  errorMessage,
  jobId,
}: PreviewPanelProps) {
  const statusText =
    jobStatus === "idle"
      ? "Waiting for upload"
      : jobStatus === "uploading"
      ? "Uploading image"
      : jobStatus === "processing"
      ? "Processing image"
      : jobStatus === "done"
      ? "Completed"
      : "Error";

  return (
    <section className="rounded-2xl border border-slate-700/60 bg-slate-900/70 p-6 shadow-lg shadow-black/20">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-cyan-300">Preview</h2>
          <p className="mt-1 text-sm text-slate-400">
            View the original image and the processed result.
          </p>
        </div>

        <span className="rounded-full border border-cyan-700/40 bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-200">
          {statusText}
        </span>
      </div>

      {jobId && (
        <div className="mb-4 rounded-xl border border-slate-800 bg-slate-950/70 p-3 text-sm text-slate-400">
          Job ID: <span className="text-slate-200">{jobId}</span>
        </div>
      )}

      {errorMessage && (
        <div className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
          {errorMessage}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-200">Original</h3>
            <span className="text-xs text-slate-500">Input</span>
          </div>

          <div className="flex aspect-[4/3] items-center justify-center overflow-hidden rounded-xl border border-dashed border-slate-700 bg-slate-900/50">
            {previewUrl ? (
              <img
                src={previewUrl}
                alt="Original preview"
                className="h-full w-full object-contain"
              />
            ) : (
              <p className="text-sm text-slate-500">Original image preview</p>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-200">Enhanced</h3>
            <span className="text-xs text-slate-500">Output</span>
          </div>

          <div className="flex aspect-[4/3] items-center justify-center overflow-hidden rounded-xl border border-dashed border-cyan-800/40 bg-slate-900/50">
            {resultUrl ? (
              <img
                src={resultUrl}
                alt="Enhanced preview"
                className="h-full w-full object-contain"
              />
            ) : (
              <p className="text-sm text-slate-500">
                {jobStatus === "uploading" || jobStatus === "processing"
                  ? "Processing..."
                  : "Processed image preview"}
              </p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}