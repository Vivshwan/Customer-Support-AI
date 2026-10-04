import { ChatWindow } from "./components/ChatWindow";
import { ChatInput } from "./components/ChatInput";
import { useChat } from "./hooks/useChat";

export default function App() {
  const { messages, isLoading, error, send } = useChat();

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-3xl h-[85vh] bg-white rounded-2xl shadow-xl flex flex-col overflow-hidden">
        {/* Header */}
        <header className="px-6 py-4 border-b bg-white">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold">
              TM
            </div>
            <div>
              <h1 className="font-semibold text-gray-900">TechMart Support</h1>
              <p className="text-xs text-gray-500">
                AI-powered multi-agent assistant
              </p>
            </div>
          </div>
        </header>

        {/* Body */}
        <ChatWindow messages={messages} isLoading={isLoading} />

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
  );
}