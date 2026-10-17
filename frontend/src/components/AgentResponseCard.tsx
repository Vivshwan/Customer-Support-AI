import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { FileText } from "lucide-react";
import type { AgentResponse } from "../types";

const AGENT_META: Record<string, { label: string; color: string }> = {
  billing:   { label: "Billing Agent",   color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
  technical: { label: "Technical Agent", color: "bg-blue-500/10 text-blue-400 border-blue-500/20" },
  product:   { label: "Product Agent",   color: "bg-purple-500/10 text-purple-400 border-purple-500/20" },
  complaint: { label: "Complaint Agent", color: "bg-orange-500/10 text-orange-400 border-orange-500/20" },
  faq:       { label: "FAQ Agent",       color: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20" },
};

export function AgentResponseCard({ response }: { response: AgentResponse }) {
  const meta = AGENT_META[response.agent] ?? {
    label: response.agent,
    color: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl rounded-tl-sm shadow-xl overflow-hidden transition-all duration-300 hover:border-zinc-700">
      <div className="px-5 py-3 border-b border-zinc-800/50 flex items-center justify-between bg-zinc-900/50">
        <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${meta.color}`}>
          {meta.label}
        </span>
      </div>
      
      <div className="px-5 py-4 text-zinc-200 prose prose-invert prose-sm max-w-none leading-relaxed">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {response.answer}
        </ReactMarkdown>
      </div>

      {response.sources.length > 0 && (
        <div className="px-5 py-3 bg-zinc-950/30 border-t border-zinc-800/50 flex flex-wrap gap-2">
          {response.sources.map((s) => (
            <span
              key={s}
              className="flex items-center gap-1.5 text-[11px] font-medium text-zinc-500 hover:text-zinc-300 transition-colors bg-zinc-900 border border-zinc-800 px-2 py-1 rounded-md"
            >
              <FileText className="w-3 h-3" />
              {s}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}