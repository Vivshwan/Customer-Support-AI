import { useState } from "react";

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
    <div className="flex gap-2 p-3 border-t bg-white">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
        placeholder="Ask about refunds, shipping, subscriptions, product info..."
        disabled={disabled}
        className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm
                   focus:outline-none focus:ring-2 focus:ring-blue-500
                   disabled:bg-gray-50"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !text.trim()}
        className="px-5 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium
                   hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed
                   transition-colors"
      >
        {disabled ? "..." : "Send"}
      </button>
    </div>
  );
}