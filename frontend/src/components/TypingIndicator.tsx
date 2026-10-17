import { Bot } from "lucide-react";

export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 animate-in fade-in duration-300">
      <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0 shadow-[0_0_15px_rgba(37,99,235,0.4)]">
        <Bot className="w-5 h-5 text-white" />
      </div>
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl rounded-tl-sm px-5 py-4 shadow-lg flex items-center gap-1.5 h-[52px]">
        <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
        <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
        <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce" />
      </div>
    </div>
  );
}