import { useState } from "react";
import { ArrowUp, Mic, MicOff } from "lucide-react";
import { useVoiceInput } from "../hooks/useVoiceInputs";

interface Props {
  onSend: (text: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: Props) {
  const [text, setText] = useState("");

  // Initialize the voice hook
  const { isListening, toggleListening, isSupported, error: voiceError } = useVoiceInput({
    onResult: (transcript) => {
      // FIX: Replace the text entirely instead of appending it.
      // This prevents partial sentences from stacking up.
      setText(transcript);
    },
  });

  const handleSend = () => {
    if (!text.trim() || disabled) return;
    onSend(text);
    setText("");
  };

  return (
    <div className="p-4 bg-zinc-950 border-t border-zinc-800/50 flex flex-col items-center">
      
      {/* Voice Error Message */}
      {voiceError && (
        <p className="text-red-400 text-xs mb-2 animate-in fade-in">{voiceError}</p>
      )}

      <div className="w-full max-w-3xl relative flex items-center bg-zinc-900 border border-zinc-800 rounded-xl focus-within:ring-2 focus-within:ring-blue-500/50 transition-all shadow-lg pl-2">
        
        {/* Microphone Button */}
        {isSupported && (
          <button
            onClick={toggleListening}
            disabled={disabled}
            title={isListening ? "Stop listening" : "Start voice input"}
            className={`p-2 rounded-lg transition-all duration-300 shrink-0 ${
              isListening 
                ? "bg-red-500/20 text-red-500 animate-pulse" 
                : "text-zinc-500 hover:text-blue-400 hover:bg-zinc-800"
            }`}
          >
            {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>
        )}

        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder={isListening ? "Listening..." : "Ask about refunds, shipping, products..."}
          disabled={disabled || isListening}
          className="flex-1 bg-transparent text-zinc-100 placeholder-zinc-500 px-3 py-4 text-sm focus:outline-none disabled:opacity-50"
        />
        
        <button
          onClick={handleSend}
          disabled={disabled || !text.trim() || isListening}
          className="absolute right-2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-600 transition-all shadow-md"
        >
          <ArrowUp className="w-4 h-4" />
        </button>
      </div>
      
      <p className="text-center text-[10px] text-zinc-600 mt-3">
        {isListening ? "Speak now..." : "TechMart AI can make mistakes. Verify important information."}
      </p>
    </div>
  );
}