import axios from "axios";

const client = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

export async function createJob(data) {
  const response = await client.post("/pipeline/jobs", data);
  return response.data;
}

export async function getJobStatus(jobId) {
  const response = await client.get(`/pipeline/jobs/${jobId}`);
  return response.data;
}

export async function submitInterviewAnswer(jobId, answer) {
  const response = await client.post(`/pipeline/jobs/${jobId}/interview`, { answer });
  return response.data;
}

export function getReportDownloadUrl(jobId) {
  return `/api/report/${jobId}`;
}
