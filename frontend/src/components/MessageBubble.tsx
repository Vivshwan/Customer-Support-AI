import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bot, User } from "lucide-react";
import type { ChatMessage } from "../types";
import { AgentResponseCard } from "./AgentResponseCard";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
        <div className="max-w-[75%] bg-blue-600 text-white rounded-2xl rounded-tr-sm px-5 py-3 shadow-lg">
          <p className="whitespace-pre-wrap text-sm leading-relaxed">
            {message.content}
          </p>
        </div>
        <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center shrink-0 border border-zinc-700">
          <User className="w-4 h-4 text-zinc-400" />
        </div>
      </div>
    );
  }

  // assistant
  const responses = message.responses ?? [];

  return (
    <div className="flex justify-start gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
      <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0 shadow-[0_0_15px_rgba(37,99,235,0.4)]">
        <Bot className="w-5 h-5 text-white" />
      </div>

      <div className="max-w-[85%] w-full space-y-3">
        {message.intents && message.intents.length > 0 && (
          <div className="flex gap-2 text-[10px] font-medium tracking-wider uppercase text-zinc-500">
            {message.intents.map((i) => (
              <span
                key={i}
                className="bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded-full"
              >
                {i}
              </span>
            ))}
          </div>
        )}

        {responses.length > 0 ? (
          responses.map((r, idx) => (
            <AgentResponseCard key={idx} response={r} />
          ))
        ) : (
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl rounded-tl-sm px-5 py-4 shadow-lg text-zinc-200 prose prose-invert prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}