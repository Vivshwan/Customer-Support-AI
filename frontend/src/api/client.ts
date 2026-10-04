import axios from "axios";
import type {
  AuthResponse,
  ChatResponse,
  Conversation,
  User,
} from "../types";

// ---------- Config ----------
const API_BASE = "http://localhost:8000";
const TOKEN_KEY = "techmart_token";

// ---------- Axios instance ----------
export const api = axios.create({
  baseURL: API_BASE,
  timeout: 60_000,
  headers: { "Content-Type": "application/json" },
});

// ---------- Token helpers ----------
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

// ---------- Request interceptor: attach JWT ----------
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ---------- Response interceptor: auto-logout on 401 ----------
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      clearToken();
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

// ============================================================
// AUTH
// ============================================================

export async function register(
  email: string,
  password: string,
  name: string
): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/auth/register", {
    email,
    password,
    name,
  });
  return data;
}

export async function login(
  email: string,
  password: string
): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/auth/login", {
    email,
    password,
  });
  return data;
}

export async function fetchMe(): Promise<User> {
  const { data } = await api.get<{ user: User }>("/auth/me");
  return data.user;
}

// ============================================================
// CONVERSATIONS
// ============================================================

export async function listConversations(): Promise<Conversation[]> {
  const { data } = await api.get<{ conversations: Conversation[] }>(
    "/conversations"
  );
  return data.conversations;
}

export async function createConversation(title: string): Promise<Conversation> {
  const { data } = await api.post<Conversation>("/conversations", { title });
  return data;
}

export async function getConversation(
  id: string
): Promise<{ conversation: Conversation; messages: any[] }> {
  const { data } = await api.get(`/conversations/${id}`);
  return data;
}

export async function deleteConversation(id: string): Promise<void> {
  await api.delete(`/conversations/${id}`);
}

// ============================================================
// CHAT
// ============================================================

export async function sendChatMessage(
  conversationId: string,
  message: string
): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>("/chat", {
    conversation_id: conversationId,
    message,
  });
  return data;
}

// ============================================================
// HEALTH
// ============================================================

export async function healthCheck() {
  const { data } = await api.get("/health");
  return data;
}