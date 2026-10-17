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
    <div className="flex h-screen w-full bg-zinc-950 overflow-hidden">
      {/* Left: Sidebar */}
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={selectConversation}
        onNew={newConversation}
        onDelete={removeConversation}
        onLogout={logout}
        userName={user?.name}
      />

      {/* Right: Chat Area */}
      <main className="flex-1 flex flex-col relative h-full">
        {/* Header */}
        <header className="h-14 border-b border-zinc-800/50 flex items-center px-6 bg-zinc-950/80 backdrop-blur-sm sticky top-0 z-10">
          <h1 className="font-semibold text-zinc-200">Customer Support</h1>
        </header>

        {/* Chat Body */}
        {isLoadingConv ? (
          <div className="flex-1 flex items-center justify-center text-zinc-500">
            Loading conversation...
          </div>
        ) : (
          <ChatWindow messages={messages} isLoading={isLoading} />
        )}

        {/* Error Banner */}
        {error && (
          <div className="bg-red-500/10 border-t border-red-500/20 text-red-400 text-sm px-6 py-2 text-center">
            {error}
          </div>
        )}

        {/* Input */}
        <ChatInput onSend={send} disabled={isLoading} />
      </main>
    </div>
  );
}