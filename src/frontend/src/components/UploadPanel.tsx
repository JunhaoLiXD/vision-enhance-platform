import type { JobStatus } from "../App";
import type { PresetItem } from "../services/api";

type UploadPanelProps = {
  selectedFile: File | null;
  jobStatus: JobStatus;
  errorMessage: string;
  presets: PresetItem[];
  selectedPresetId: string;
  onPresetChange: (presetId: string) => void;
  onFileChange: (file: File | null) => void;
  onStartProcess: () => void;
};

export default function UploadPanel({
  selectedFile,
  jobStatus,
  errorMessage,
  presets,
  selectedPresetId,
  onPresetChange,
  onFileChange,
  onStartProcess,
}: UploadPanelProps) {
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    onFileChange(file);
  };

  const isBusy = jobStatus === "uploading" || jobStatus === "processing";

  const selectedPreset = presets.find((preset) => preset.id === selectedPresetId);

  return (
    <section className="rounded-2xl border border-slate-700/60 bg-slate-900/70 p-6 shadow-lg shadow-black/20">
      <div className="mb-5">
        <h2 className="text-xl font-semibold text-cyan-300">Upload</h2>
        <p className="mt-1 text-sm text-slate-400">
          Choose an image and a preset pipeline to start enhancement.
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
        <p className="text-sm font-medium text-slate-200">Preset pipeline</p>

        <select
          value={selectedPresetId}
          onChange={(e) => onPresetChange(e.target.value)}
          disabled={isBusy || presets.length === 0}
          className="mt-3 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {presets.length === 0 ? (
            <option value="">No presets available</option>
          ) : (
            presets.map((preset) => (
              <option key={preset.id} value={preset.id}>
                {preset.name}
              </option>
            ))
          )}
        </select>

        {selectedPreset?.description && (
          <p className="mt-3 text-sm text-slate-400">
            {selectedPreset.description}
          </p>
        )}
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
        disabled={isBusy || !selectedFile || !selectedPresetId}
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