import { useState } from "react";
import { ArrowUp } from "lucide-react";

interface Props {
  onSend: (text: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: Props) {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (!text.trim() || disabled) return;
    onSend(text);
    setText("");
  };

  return (
    <div className="p-4 bg-zinc-950 border-t border-zinc-800/50">
      <div className="max-w-3xl mx-auto relative flex items-center bg-zinc-900 border border-zinc-800 rounded-xl focus-within:ring-2 focus-within:ring-blue-500/50 transition-all shadow-lg">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask about refunds, shipping, products..."
          disabled={disabled}
          className="flex-1 bg-transparent text-zinc-100 placeholder-zinc-500 px-5 py-4 text-sm focus:outline-none disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={disabled || !text.trim()}
          className="absolute right-2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-600 transition-all shadow-md"
        >
          <ArrowUp className="w-4 h-4" />
        </button>
      </div>
      <p className="text-center text-[10px] text-zinc-600 mt-3">
        TechMart AI can make mistakes. Verify important information.
      </p>
    </div>
  );
}