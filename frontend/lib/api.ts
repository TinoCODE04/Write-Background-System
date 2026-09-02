import type { ImageAsset, Job, ProcessingSettings, SystemInfo, UploadResponse } from "@/types/api";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { ...init, cache: "no-store" });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: response.statusText }));
    const detail = typeof payload.detail === "string" ? payload.detail : JSON.stringify(payload.detail);
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  listJobs: () => request<Job[]>("/api/jobs"),
  createJob: (name?: string) => request<Job>("/api/jobs", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name }) }),
  getJob: (id: string) => request<Job>(`/api/jobs/${id}`),
  uploadImages: (id: string, files: File[]) => {
    const body = new FormData(); files.forEach((file) => body.append("files", file));
    return request<UploadResponse>(`/api/jobs/${id}/images`, { method: "POST", body });
  },
  processJob: (id: string) => request<Job>(`/api/jobs/${id}/process`, { method: "POST" }),
  listImages: (id: string) => request<ImageAsset[]>(`/api/jobs/${id}/images`),
  getImage: (id: string) => request<ImageAsset>(`/api/images/${id}`),
  updateSettings: (id: string, settings: ProcessingSettings) => request<ImageAsset>(`/api/images/${id}/settings`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(settings) }),
  reprocess: (id: string) => request<ImageAsset>(`/api/images/${id}/reprocess`, { method: "POST" }),
  approve: (id: string) => request<ImageAsset>(`/api/images/${id}/approve`, { method: "POST" }),
  system: () => request<SystemInfo>("/api/system"),
  assetUrl: (id: string, variant: "original" | "transparent" | "white.png" | "white.jpg" | "mask" | "thumbnail", download = false) => `${API_URL}/api/images/${id}/${variant}${download ? "?download=true" : ""}`,
  downloadJob: async (id: string, format: string) => {
    const response = await fetch(`${API_URL}/api/jobs/${id}/download`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ format }) });
    if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? "Download failed");
    const blob = await response.blob();
    const url = URL.createObjectURL(blob); const anchor = document.createElement("a");
    anchor.href = url; anchor.download = `batch-${id.slice(0, 8)}-${format}.zip`; anchor.click();
    URL.revokeObjectURL(url);
  }
};

