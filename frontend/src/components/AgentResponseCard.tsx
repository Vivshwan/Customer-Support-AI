import type { AgentResponse } from "../types";

const AGENT_META: Record<string, { label: string; color: string }> = {
  billing:   { label: "Billing",   color: "bg-emerald-100 text-emerald-800" },
  technical: { label: "Technical", color: "bg-blue-100 text-blue-800" },
  product:   { label: "Product",   color: "bg-purple-100 text-purple-800" },
  complaint: { label: "Complaint", color: "bg-orange-100 text-orange-800" },
  faq:       { label: "FAQ",       color: "bg-gray-100 text-gray-800" },
};

export function AgentResponseCard({ response }: { response: AgentResponse }) {
  const meta = AGENT_META[response.agent] ?? {
    label: response.agent,
    color: "bg-gray-100 text-gray-800",
  };

  return (
    <div className="border border-gray-200 rounded-lg p-3 bg-white shadow-sm">
      <div className="mb-2">
        <span className={`text-xs font-semibold px-2 py-0.5 rounded ${meta.color}`}>
          {meta.label} Agent
        </span>
      </div>
      <p className="text-gray-800 whitespace-pre-wrap text-sm leading-relaxed">
        {response.answer}
      </p>
      {response.sources.length > 0 && (
        <div className="mt-2 pt-2 border-t border-gray-100 flex flex-wrap gap-1">
          {response.sources.map((s) => (
            <span
              key={s}
              className="text-[10px] bg-gray-50 text-gray-600 px-1.5 py-0.5 rounded border border-gray-200"
            >
              📄 {s}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}