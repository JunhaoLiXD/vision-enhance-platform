const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export type JobStatus = "idle" | "uploading" | "processing" | "done" | "error";

export type CreateJobResponse = {
  job_id: string;
};

export type JobStatusResponse = {
  job_id: string;
  status: string;
};

export type ArtifactItem =
  | string
  | {
      name?: string;
      filename?: string;
      file_name?: string;
    };

export type ArtifactsResponse = {
  artifacts?: ArtifactItem[];
  outputs?: ArtifactItem[];
  files?: ArtifactItem[];
};

export type PresetItem = {
  id: string;
  name: string;
  description?: string;
  steps?: Array<{
    name: string;
    params?: Record<string, unknown>;
  }>;
};

export type AlgorithmParamSpec = {
  type: string;
  default: unknown;
  min?: number;
  max?: number;
};

export type AlgorithmItem = {
  id: string;
  name: string;
  description?: string;
  params: Record<string, AlgorithmParamSpec>;
};

export async function fetchPresets(): Promise<PresetItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/presets`);

  if (!response.ok) {
    throw new Error("Failed to fetch presets.");
  }

  const data = await response.json();

  if (Array.isArray(data.presets)) {
    return data.presets;
  }

  return Object.keys(data).map((key) => ({
    id: key,
    name: key,
    steps: data[key],
  }));
}

export async function fetchAlgorithms(): Promise<AlgorithmItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/algorithms`);

  if (!response.ok) {
    throw new Error("Failed to fetch algorithms.");
  }

  const data = await response.json();

  return Object.keys(data).map((key) => ({
    id: key,
    name: key,
    description: data[key].description,
    params: data[key].params ?? {},
  }));
}

type CreateJobOptions = {
  presetId?: string;
  pipelineSpecJson?: string;
};

export async function createJob(
  file: File,
  options: CreateJobOptions
): Promise<CreateJobResponse> {
  const formData = new FormData();
  formData.append("file", file);

  if (options.presetId){
    formData.append("preset_id", options.presetId);
  }

  if (options.pipelineSpecJson){
    formData.append("pipeline_spec_json", options.pipelineSpecJson);
  }

  const response = await fetch(`${API_BASE_URL}/api/jobs`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to create job.");
  }

  return response.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`);

  if (!response.ok) {
    throw new Error("Failed to fetch job status.");
  }

  return response.json();
}

export async function getJobArtifacts(jobId: string): Promise<ArtifactsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/artifacts`);

  if (!response.ok) {
    throw new Error("Failed to fetch job artifacts.");
  }

  return response.json();
}

export function buildDownloadUrl(jobId: string, name: string): string {
  return `${API_BASE_URL}/api/jobs/${jobId}/download/${encodeURIComponent(name)}`;
}