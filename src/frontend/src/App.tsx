import { useEffect, useState } from "react";
import UploadPanel from "./components/UploadPanel";
import PreviewPanel from "./components/PreviewPanel";
import DownloadPanel from "./components/DownloadPanel";
import AlgorithmConfigPanel from "./components/AlgorithmConfigPanel";

import {
  createJob,
  getJobStatus,
  getJobArtifacts,
  buildDownloadUrl,
  fetchPresets,
  fetchAlgorithms,
  type PresetItem,
  type AlgorithmItem,
} from "./services/api";

export type JobStatus = "idle" | "uploading" | "processing" | "done" | "error";

export default function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");

  const [jobId, setJobId] = useState<string>("");
  const [jobStatus, setJobStatus] = useState<JobStatus>("idle");

  const [resultUrl, setResultUrl] = useState<string>("");
  const [downloadName, setDownloadName] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>("");

  const [mode, setMode] = useState<"preset" | "custom">("preset");

  const [presets, setPresets] = useState<PresetItem[]>([]);
  const [selectedPresetId, setSelectedPresetId] = useState<string>("");

  const [algorithms, setAlgorithms] = useState<AlgorithmItem[]>([]);
  const [selectedAlgorithmId, setSelectedAlgorithmId] = useState<string>("");
  const [algorithmParams, setAlgorithmParams] = useState<Record<string, unknown>>({});

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [presetList, algorithmList] = await Promise.all([
          fetchPresets(),
          fetchAlgorithms(),
        ]);

        setPresets(presetList);
        if (presetList.length > 0) {
          setSelectedPresetId(presetList[0].id);
        }

        setAlgorithms(algorithmList);
        if (algorithmList.length > 0) {
          const firstAlgorithm = algorithmList[0];
          setSelectedAlgorithmId(firstAlgorithm.id);

          const defaultParams: Record<string, unknown> = {};
          Object.entries(firstAlgorithm.params).forEach(([paramName, spec]) => {
            defaultParams[paramName] = spec.default;
          });
          setAlgorithmParams(defaultParams);
        }
      } catch (error) {
        setErrorMessage(
          error instanceof Error ? error.message : "Failed to load initial data."
        );
      }
    };

    loadInitialData();
  }, []);

  const handleAlgorithmChange = (algorithmId: string) => {
    setSelectedAlgorithmId(algorithmId);

    const selectedAlgorithm = algorithms.find((item) => item.id === algorithmId);
    if (!selectedAlgorithm) return;

    const defaultParams: Record<string, unknown> = {};
    Object.entries(selectedAlgorithm.params).forEach(([paramName, spec]) => {
      defaultParams[paramName] = spec.default;
    });

    setAlgorithmParams(defaultParams);
  };

  const handleParamChange = (paramName: string, value: unknown) => {
    setAlgorithmParams((prev) => ({
      ...prev,
      [paramName]: value,
    }));
  };

  const pollJobUntilComplete = async (currentJobId: string) => {
    try {
      const maxAttempts = 30;
      const intervalMs = 1500;

      for (let attempt = 0; attempt < maxAttempts; attempt++) {
        const statusResult = await getJobStatus(currentJobId);
        const status = statusResult.status;

        if (status === "done" || status === "completed") {
          const artifactsResult = await getJobArtifacts(currentJobId);

          const artifacts =
            artifactsResult.artifacts ??
            artifactsResult.outputs ??
            artifactsResult.files ??
            [];

          const firstArtifact = artifacts[0];

          if (!firstArtifact) {
            throw new Error("Job completed but no output artifact was found.");
          }

          const artifactName =
            typeof firstArtifact === "string"
              ? firstArtifact
              : firstArtifact.name ??
                firstArtifact.filename ??
                firstArtifact.file_name ??
                "";

          if (!artifactName) {
            throw new Error("Artifact exists, but no valid artifact filename was found.");
          }

          setDownloadName(artifactName);
          setResultUrl(buildDownloadUrl(currentJobId, artifactName));
          setJobStatus("done");
          return;
        }

        if (status === "error" || status === "failed") {
          throw new Error("Image processing failed on the backend.");
        }

        await new Promise((resolve) => setTimeout(resolve, intervalMs));
      }

      throw new Error("Processing timed out.");
    } catch (error) {
      setJobStatus("error");
      setErrorMessage(
        error instanceof Error ? error.message : "Failed while polling job status."
      );
    }
  };

  const handleFileChange = (file: File | null) => {
    setSelectedFile(file);
    setErrorMessage("");
    setResultUrl("");
    setDownloadName("");
    setJobId("");
    setJobStatus("idle");

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    if (file) {
      const objectUrl = URL.createObjectURL(file);
      setPreviewUrl(objectUrl);
    } else {
      setPreviewUrl("");
    }
  };

  const handleStartProcess = async () => {
    if (!selectedFile) {
      setErrorMessage("Please select an image first.");
      setJobStatus("error");
      return;
    }

    try {
      setErrorMessage("");
      setResultUrl("");
      setDownloadName("");
      setJobId("");
      setJobStatus("uploading");

      let createResult;

      if (mode === "preset") {
        if (!selectedPresetId) {
          setErrorMessage("Please select a preset.");
          setJobStatus("error");
          return;
        }

        createResult = await createJob(selectedFile, {
          presetId: selectedPresetId,
        });
      } else {
        if (!selectedAlgorithmId) {
          setErrorMessage("Please select an algorithm.");
          setJobStatus("error");
          return;
        }

        const pipelineSpecJson = JSON.stringify([
          {
            name: selectedAlgorithmId,
            params: algorithmParams,
          },
        ]);

        createResult = await createJob(selectedFile, {
          pipelineSpecJson,
        });
      }

      const newJobId = createResult.job_id;

      if (!newJobId) {
        throw new Error("Backend did not return a valid job id.");
      }

      setJobId(newJobId);
      setJobStatus("processing");

      pollJobUntilComplete(newJobId);
    } catch (error) {
      setJobStatus("error");
      setErrorMessage(
        error instanceof Error ? error.message : "Failed to create job."
      );
    }
  };

  const handleDownload = async () => {
    if (!resultUrl) return;

    try {
      const response = await fetch(resultUrl);

      if (!response.ok) {
        throw new Error("Failed to download the result file.");
      }

      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = downloadName || "result.png";
      document.body.appendChild(link);
      link.click();
      link.remove();

      URL.revokeObjectURL(blobUrl);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Download failed."
      );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-cyan-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-10 lg:px-8">
        <header className="mb-8">
          <div className="inline-flex items-center rounded-full border border-cyan-700/40 bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-200">
            Vision Enhance Platform
          </div>

          <h1 className="mt-4 text-4xl font-bold tracking-tight text-white md:text-5xl">
            Image Enhancement Studio
          </h1>

          <p className="mt-3 max-w-2xl text-base text-slate-300 md:text-lg">
            Upload an image, preview the enhancement workflow, and download the
            processed result from a clean local web interface.
          </p>
        </header>

        <main className="grid gap-6 lg:grid-cols-12">
          <div className="space-y-6 lg:col-span-4">
            <UploadPanel
              selectedFile={selectedFile}
              jobStatus={jobStatus}
              errorMessage={errorMessage}
              presets={presets}
              selectedPresetId={selectedPresetId}
              mode={mode}
              onModeChange={setMode}
              onPresetChange={setSelectedPresetId}
              onFileChange={handleFileChange}
              onStartProcess={handleStartProcess}
            />

            <DownloadPanel
              jobStatus={jobStatus}
              downloadName={downloadName}
              onDownload={handleDownload}
            />
          </div>

          <div className="space-y-6 lg:col-span-8">
            <PreviewPanel
              previewUrl={previewUrl}
              resultUrl={resultUrl}
              jobStatus={jobStatus}
              errorMessage={errorMessage}
              jobId={jobId}
            />

            <AlgorithmConfigPanel
              isCustomMode={mode === "custom"}
              algorithms={algorithms}
              selectedAlgorithmId={selectedAlgorithmId}
              algorithmParams={algorithmParams}
              onAlgorithmChange={handleAlgorithmChange}
              onParamChange={handleParamChange}
            />
          </div>
        </main>
      </div>
    </div>
  );
}