import axios from "axios";
import type { ChatResponse } from "../types";

const API_BASE = "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 60_000,
  headers: { "Content-Type": "application/json" },
});

export async function sendMessage(
  sessionId: string,
  message: string
): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>("/chat", {
    session_id: sessionId,
    message,
  });
  return data;
}

export async function healthCheck() {
  const { data } = await api.get("/health");
  return data;
}