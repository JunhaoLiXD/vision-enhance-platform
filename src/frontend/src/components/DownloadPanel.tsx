import type { JobStatus } from "../App";

type DownloadPanelProps = {
  jobStatus: JobStatus;
  downloadName: string;
  onDownload: () => void;
};

export default function DownloadPanel({
  jobStatus,
  downloadName,
  onDownload,
}: DownloadPanelProps) {
  const canDownload = jobStatus === "done" && !!downloadName;

  return (
    <section className="rounded-2xl border border-slate-700/60 bg-slate-900/70 p-6 shadow-lg shadow-black/20">
      <div className="mb-5">
        <h2 className="text-xl font-semibold text-cyan-300">Download</h2>
        <p className="mt-1 text-sm text-slate-400">
          Download the enhanced result when processing is complete.
        </p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
        <p className="text-sm font-medium text-slate-200">Result status</p>
        <p className="mt-1 text-sm text-slate-400">
          {canDownload
            ? `Ready: ${downloadName}`
            : "No processed result available yet."}
        </p>
      </div>

      <button
        onClick={onDownload}
        disabled={!canDownload}
        className="mt-5 w-full rounded-xl bg-cyan-500 px-4 py-3 font-medium text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-300 disabled:opacity-60"
      >
        Download Result
      </button>
    </section>
  );
}