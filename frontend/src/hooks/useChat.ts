import { useCallback, useEffect, useState } from "react";
import {
  createConversation,
  deleteConversation,
  getConversation,
  listConversations,
  sendChatMessage,
} from "../api/client";
import type { ChatMessage, Conversation } from "../types";

const ACTIVE_CONV_KEY = "techmart_active_conversation";

export function useChat() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(() =>
    localStorage.getItem(ACTIVE_CONV_KEY)
  );
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingConv, setIsLoadingConv] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ---------- Load list of conversations on mount ----------
  useEffect(() => {
    refreshConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---------- Whenever activeId changes, load its messages ----------
  useEffect(() => {
    if (!activeId) {
      setMessages([]);
      return;
    }
    loadConversation(activeId);
  }, [activeId]);

  // ---------- Persist active id ----------
  useEffect(() => {
    if (activeId) localStorage.setItem(ACTIVE_CONV_KEY, activeId);
  }, [activeId]);

  const refreshConversations = useCallback(async () => {
    try {
      const list = await listConversations();
      setConversations(list);
      // Auto-select the most recent if none selected
      if (!activeId && list.length > 0) {
        setActiveId(list[0]._id);
      }
    } catch (e) {
      console.error("Failed to load conversations:", e);
    }
  }, [activeId]);

  const loadConversation = useCallback(async (id: string) => {
    setIsLoadingConv(true);
    setError(null);
    try {
      const { messages: raw } = await getConversation(id);
      // Convert backend messages to ChatMessage shape
      const mapped: ChatMessage[] = raw.map((m: any) => ({
        id: m._id,
        role: m.role,
        content: m.content,
        intents: m.intents,
        responses:
          m.role === "assistant" && m.intents
            ? [
                {
                  // Reconstruct a single agent response for display
                  // (stored as combined text with [AGENT] prefixes)
                  agent: (m.intents[0] as string) || "faq",
                  answer: m.content,
                  sources: m.sources || [],
                },
              ]
            : undefined,
        timestamp: m.timestamp,
      }));
      setMessages(mapped);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to load conversation.");
    } finally {
      setIsLoadingConv(false);
    }
  }, []);

  const newConversation = useCallback(async () => {
    try {
      const conv = await createConversation("New chat");
      setConversations((prev) => [conv, ...prev]);
      setActiveId(conv._id);
      setMessages([]);
      return conv;
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to create conversation.");
      return null;
    }
  }, []);

  const selectConversation = useCallback((id: string) => {
    setActiveId(id);
  }, []);

  const removeConversation = useCallback(
    async (id: string) => {
      try {
        await deleteConversation(id);
        setConversations((prev) => prev.filter((c) => c._id !== id));
        if (activeId === id) {
          const remaining = conversations.filter((c) => c._id !== id);
          setActiveId(remaining[0]?._id ?? null);
        }
      } catch (e: any) {
        setError(e?.response?.data?.detail || "Failed to delete conversation.");
      }
    },
    [activeId, conversations]
  );

  const send = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isLoading) return;

      // Auto-create a conversation if none exists
      let convId = activeId;
      if (!convId) {
        const conv = await newConversation();
        if (!conv) return;
        convId = conv._id;
      }

      setError(null);
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmed,
        timestamp: new Date().toISOString(),
      };
      setMessages((m) => [...m, userMsg]);
      setIsLoading(true);

      try {
        const res = await sendChatMessage(convId, trimmed);
        const aiMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: res.responses.length === 1 ? res.responses[0].answer : "",
          intents: res.intents,
          responses: res.responses,
          timestamp: res.timestamp,
        };
        setMessages((m) => [...m, aiMsg]);

        // Refresh sidebar (title may have been auto-updated by backend)
        refreshConversations();
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
    [activeId, isLoading, newConversation, refreshConversations]
  );

  return {
    conversations,
    activeId,
    messages,
    isLoading,
    isLoadingConv,
    error,
    send,
    newConversation,
    selectConversation,
    removeConversation,
  };
}