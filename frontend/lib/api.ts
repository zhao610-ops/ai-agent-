export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers: { "Content-Type": "application/json", ...options?.headers }, cache: "no-store" });
  if (!response.ok) {
    // FastAPI 的错误信息位于 detail 字段，统一提取后供页面直接提示。
    const body = await response.text();
    let message = body || `请求失败：${response.status}`;
    try { message = (JSON.parse(body) as { detail?: string }).detail || message; } catch { /* 非 JSON 响应保留原文。 */ }
    throw new Error(message);
  }
  return response.json();
}
