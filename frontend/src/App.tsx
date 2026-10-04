import { ChatWindow } from "./components/ChatWindow";
import { ChatInput } from "./components/ChatInput";
import { Sidebar } from "./components/Sidebar";
import { useChat } from "./hooks/useChat";
import { useAuth } from "./auth/AuthContext";

export default function App() {
  const {
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
  } = useChat();
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Left: sidebar */}
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={selectConversation}
        onNew={newConversation}
        onDelete={removeConversation}
        onLogout={logout}
        userName={user?.name}
      />

      {/* Right: chat */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-3xl h-[90vh] bg-white rounded-2xl shadow-xl flex flex-col overflow-hidden">
          {/* Header */}
          <header className="px-6 py-4 border-b bg-white">
            <h1 className="font-semibold text-gray-900">TechMart Support</h1>
            <p className="text-xs text-gray-500">
              {user ? `Signed in as ${user.name}` : "AI multi-agent assistant"}
            </p>
          </header>

          {/* Body */}
          {isLoadingConv ? (
            <div className="flex-1 flex items-center justify-center text-gray-400">
              Loading conversation...
            </div>
          ) : (
            <ChatWindow messages={messages} isLoading={isLoading} />
          )}

          {/* Error banner */}
          {error && (
            <div className="px-4 py-2 bg-red-50 text-red-700 text-sm border-t border-red-200">
              ⚠️ {error}
            </div>
          )}

          {/* Input */}
          <ChatInput onSend={send} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}