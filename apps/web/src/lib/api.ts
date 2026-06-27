const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(data.detail || "Request failed");
  }

  return response.json() as Promise<T>;
}

