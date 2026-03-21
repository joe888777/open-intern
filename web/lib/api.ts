const BASE = "/api/dashboard";

export async function getStatus() {
  const res = await fetch(`${BASE}/status`);
  if (!res.ok) throw new Error("Failed to fetch status");
  return res.json();
}

export async function getConfig() {
  const res = await fetch(`${BASE}/config`);
  if (!res.ok) throw new Error("Failed to fetch config");
  return res.json();
}

export async function updateIdentity(data: {
  name: string;
  role: string;
  personality: string;
  avatar_url?: string;
}) {
  const res = await fetch(`${BASE}/config/identity`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update identity");
  return res.json();
}

export async function updateLLM(data: {
  provider: string;
  model: string;
  temperature: number;
  max_tokens_per_action: number;
  daily_cost_budget_usd: number;
}) {
  const res = await fetch(`${BASE}/config/llm`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update LLM config");
  return res.json();
}

export async function sendMessage(message: string, threadId?: string): Promise<{ response: string; thread_id: string; title: string }> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, thread_id: threadId || "" }),
  });
  if (!res.ok) throw new Error("Failed to send message");
  return res.json();
}

export async function getThreads(): Promise<{ threads: { thread_id: string; title: string; created_at: string }[] }> {
  const res = await fetch(`${BASE}/threads`);
  if (!res.ok) throw new Error("Failed to fetch threads");
  return res.json();
}

export async function updateThreadTitle(threadId: string, title: string) {
  const res = await fetch(`${BASE}/threads/${threadId}/title`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error("Failed to update thread title");
  return res.json();
}

export async function deleteThread(threadId: string) {
  const res = await fetch(`${BASE}/threads/${threadId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete thread");
  return res.json();
}

export async function getMemories(scope?: string, limit = 50, offset = 0) {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (scope) params.set("scope", scope);
  const res = await fetch(`${BASE}/memories?${params}`);
  if (!res.ok) throw new Error("Failed to fetch memories");
  return res.json();
}

export async function getMemoryStats() {
  const res = await fetch(`${BASE}/memories/stats`);
  if (!res.ok) throw new Error("Failed to fetch memory stats");
  return res.json();
}

export async function deleteMemory(id: string) {
  const res = await fetch(`${BASE}/memories/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete memory");
  return res.json();
}
