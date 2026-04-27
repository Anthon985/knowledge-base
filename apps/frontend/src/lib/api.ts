const API_BASE = "/api/v1";

export interface Document {
  id: string;
  filename: string;
  original_filename: string;
  content_type: string;
  file_size: number;
  status: "pending" | "processing" | "completed" | "failed";
  chunk_count: number;
  error_message: string | null;
  workflow_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface SearchHit {
  document_id: string;
  chunk_index: number;
  content: string;
  filename: string;
  score: number;
}

export interface ChatResponse {
  answer: string;
  sources: { filename: string; document_id: string }[];
}

export async function uploadDocument(file: File): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function listDocuments(skip = 0, limit = 20): Promise<{ documents: Document[]; total: number }> {
  const res = await fetch(`${API_BASE}/documents?skip=${skip}&limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

export async function getDocument(id: string): Promise<Document> {
  const res = await fetch(`${API_BASE}/documents/${id}`);
  if (!res.ok) throw new Error("Document not found");
  return res.json();
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete");
}

export async function searchDocuments(query: string, topK = 10): Promise<{ hits: SearchHit[]; total: number }> {
  const res = await fetch(`${API_BASE}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK }),
  });
  if (!res.ok) throw new Error("Search failed");
  return res.json();
}

export async function chatWithKB(query: string, topK = 5): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK }),
  });
  if (!res.ok) throw new Error("Chat failed");
  return res.json();
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

export function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString("zh-CN", { year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "completed": return "text-success";
    case "processing": return "text-warning";
    case "failed": return "text-destructive";
    default: return "text-muted-foreground";
  }
}

export function getStatusLabel(status: string): string {
  switch (status) {
    case "completed": return "已完成";
    case "processing": return "处理中";
    case "failed": return "失败";
    case "pending": return "等待中";
    default: return status;
  }
}