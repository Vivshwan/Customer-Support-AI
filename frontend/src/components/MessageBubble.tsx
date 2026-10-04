import type { ChatMessage } from "../types";
import { AgentResponseCard } from "./AgentResponseCard";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[70%] bg-blue-600 text-white rounded-2xl rounded-br-md px-4 py-2 shadow">
          <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        </div>
      </div>
    );
  }

  // assistant — may be multi-agent
  const responses = message.responses ?? [];

  return (
    <div className="flex justify-start">
      <div className="max-w-[85%] w-full space-y-2">
        {message.intents && message.intents.length > 0 && (
          <div className="flex gap-1 text-[10px] text-gray-500">
            {message.intents.map((i) => (
              <span
                key={i}
                className="bg-gray-100 px-1.5 py-0.5 rounded uppercase tracking-wide"
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
          <div className="bg-white border rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
            <p className="whitespace-pre-wrap text-sm text-gray-800">
              {message.content}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}