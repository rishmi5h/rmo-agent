export interface ConfigEntry {
  id: number;
  service_name: string;
  environment: "dev" | "staging" | "prod";
  config_key: string;
  config_value: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface ToolCallInfo {
  tool: string;
  input: Record<string, unknown>;
}

export interface AgentResponse {
  reply: string;
  tool_calls: ToolCallInfo[] | null;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  tool_calls?: ToolCallInfo[];
}
