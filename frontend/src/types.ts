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

export interface Conversation {
  _id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface AgentResponse {
  agent: string;
  answer: string;
  sources: string[];
}

export interface ChatResponse {
  conversation_id: string;
  query: string;
  intents: string[];
  responses: AgentResponse[];
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  intents?: string[];
  responses?: AgentResponse[];
  timestamp: string;
}