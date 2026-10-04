// Types matching the FastAPI backend schema

export interface AgentResponse {
  agent: string;
  answer: string;
  sources: string[];
}

export interface ChatResponse {
  session_id: string;
  query: string;
  intents: string[];
  responses: AgentResponse[];
  timestamp: string;
}

export interface ChatMessage {
  id: string;                       // client-side unique id
  role: "user" | "assistant";
  content: string;                  // for user messages OR fallback text
  intents?: string[];               // assistant only
  responses?: AgentResponse[];      // assistant only (multi-agent)
  timestamp: string;
}

export interface User {
  _id: string;
  email: string;
  name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}