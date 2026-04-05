import type { JobStatus } from "../App";

type UploadPanelProps = {
  selectedFile: File | null;
  jobStatus: JobStatus;
  errorMessage: string;
  onFileChange: (file: File | null) => void;
  onStartProcess: () => void;
};

export default function UploadPanel({
  selectedFile,
  jobStatus,
  errorMessage,
  onFileChange,
  onStartProcess,
}: UploadPanelProps) {
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    onFileChange(file);
  };

  const isBusy = jobStatus === "uploading" || jobStatus === "processing";

  return (
    <section className="rounded-2xl border border-slate-700/60 bg-slate-900/70 p-6 shadow-lg shadow-black/20">
      <div className="mb-5">
        <h2 className="text-xl font-semibold text-cyan-300">Upload</h2>
        <p className="mt-1 text-sm text-slate-400">
          Choose an image to start the enhancement workflow.
        </p>
      </div>

      <div className="rounded-xl border border-dashed border-cyan-700/50 bg-slate-950/60 p-6 text-center">
        <div className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-cyan-500/10 text-2xl text-cyan-300">
          ⤴
        </div>

        <p className="text-sm text-slate-300">Select an image from your device</p>
        <p className="mt-1 text-xs text-slate-500">PNG, JPG, JPEG, WEBP</p>

        <label className="mt-5 inline-block cursor-pointer rounded-xl bg-cyan-500 px-4 py-2 font-medium text-slate-950 transition hover:bg-cyan-400">
          Select Image
          <input
            type="file"
            accept="image/png,image/jpeg,image/jpg,image/webp"
            className="hidden"
            onChange={handleInputChange}
          />
        </label>
      </div>

      <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
        <p className="text-sm font-medium text-slate-200">Current file</p>
        <p className="mt-1 break-all text-sm text-slate-400">
          {selectedFile ? selectedFile.name : "No file selected"}
        </p>
      </div>

      <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
        <p className="text-sm font-medium text-slate-200">Current status</p>
        <p className="mt-1 text-sm text-slate-400">{jobStatus}</p>
      </div>

      {errorMessage && (
        <div className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
          {errorMessage}
        </div>
      )}

      <button
        onClick={onStartProcess}
        disabled={isBusy}
        className="mt-5 w-full rounded-xl bg-cyan-500 px-4 py-3 font-medium text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {jobStatus === "uploading"
          ? "Uploading..."
          : jobStatus === "processing"
          ? "Processing..."
          : "Start Enhancement"}
      </button>
    </section>
  );
}