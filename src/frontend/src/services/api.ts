const API_BASE_URL = "http://127.0.0.1:8000";

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

export async function createJob(file: File): Promise<CreateJobResponse> {
  const formData = new FormData();
  formData.append("file", file);

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