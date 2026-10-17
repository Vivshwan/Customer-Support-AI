import { useEffect, useRef } from "react";
import { Sparkles } from "lucide-react";
import type { ChatMessage } from "../types";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";

interface Props {
  messages: ChatMessage[];
  isLoading: boolean;
}

export function ChatWindow({ messages, isLoading }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 bg-zinc-950">
      {messages.length === 0 && (
        <div className="h-full flex flex-col items-center justify-center text-center animate-in fade-in duration-700">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-purple-600 flex items-center justify-center mb-6 shadow-2xl">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-semibold text-zinc-100 mb-2">
            How can I help you today?
          </h2>
          <p className="text-sm text-zinc-400 max-w-sm">
            I can help with billing, technical issues, product information, or complaints.
          </p>
        </div>
      )}
      
      <div className="max-w-3xl mx-auto space-y-6 pb-4">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}