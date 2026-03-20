import type { ConfigEntry, AgentResponse } from "../types";

const API_BASE = "/api";
const AGENT_BASE = "/agent";

export async function getConfigs(filters?: {
  service_name?: string;
  environment?: string;
}): Promise<ConfigEntry[]> {
  const params = new URLSearchParams();
  if (filters?.service_name) params.set("service_name", filters.service_name);
  if (filters?.environment) params.set("environment", filters.environment);

  const query = params.toString();
  const url = `${API_BASE}/configs${query ? `?${query}` : ""}`;
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`Failed to fetch configs: ${resp.statusText}`);
  return resp.json();
}

export async function getServices(): Promise<string[]> {
  const resp = await fetch(`${API_BASE}/configs/services`);
  if (!resp.ok) throw new Error("Failed to fetch services");
  return resp.json();
}

export async function getEnvironments(): Promise<string[]> {
  const resp = await fetch(`${API_BASE}/configs/environments`);
  if (!resp.ok) throw new Error("Failed to fetch environments");
  return resp.json();
}

export async function sendAgentMessage(
  message: string,
  sessionId: string
): Promise<AgentResponse> {
  const resp = await fetch(`${AGENT_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  if (!resp.ok) throw new Error(`Agent request failed: ${resp.statusText}`);
  return resp.json();
}
