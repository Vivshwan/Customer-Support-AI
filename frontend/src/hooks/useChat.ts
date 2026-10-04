import { useCallback, useState } from "react";
import { sendMessage } from "../api/client";
import type { ChatMessage } from "../types";

const SESSION_KEY = "techmart_session_id";

function getOrCreateSessionId(): string {
  const existing = localStorage.getItem(SESSION_KEY);
  if (existing) return existing;
  const newId = crypto.randomUUID();
  localStorage.setItem(SESSION_KEY, newId);
  return newId;
}

export function useChat() {
  const [sessionId] = useState<string>(() => getOrCreateSessionId());
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isLoading) return;

      setError(null);

      // 1. Add user message immediately
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmed,
        timestamp: new Date().toISOString(),
      };
      setMessages((m) => [...m, userMsg]);
      setIsLoading(true);

      try {
        // 2. Call backend
        const res = await sendMessage(sessionId, trimmed);

        // 3. Add assistant message
        const aiMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: res.responses.length === 1 ? res.responses[0].answer : "",
          intents: res.intents,
          responses: res.responses,
          timestamp: res.timestamp,
        };
        setMessages((m) => [...m, aiMsg]);
      } catch (e: any) {
        const msg =
          e?.response?.data?.detail ||
          e?.message ||
          "Something went wrong. Please try again.";
        setError(msg);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, isLoading]
  );

  return { messages, isLoading, error, sessionId, send };
}