import { Link, useLocation } from "react-router-dom";
import { MessageSquarePlus, BarChart3, LogOut, MessageSquare, Trash2 } from "lucide-react";
import type { Conversation } from "../types";

interface Props {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  onLogout: () => void;
  userName?: string;
}

export function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
  onLogout,
  userName,
}: Props) {
  const location = useLocation();
  const isAnalytics = location.pathname === "/dashboard";

  return (
    <aside className="w-64 bg-zinc-950 border-r border-zinc-800/50 text-zinc-300 flex flex-col h-full z-10 shrink-0">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800/50">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-blue-400 flex items-center justify-center font-bold text-white shadow-lg">
            TM
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-white truncate">TechMart</p>
            <p className="text-[10px] text-zinc-500 truncate">{userName}</p>
          </div>
        </div>

        <button
          onClick={onNew}
          className="w-full flex items-center justify-center gap-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-white text-sm rounded-lg py-2.5 font-medium transition-all group"
        >
          <MessageSquarePlus className="w-4 h-4 text-zinc-400 group-hover:text-blue-400 transition-colors" />
          New chat
        </button>
      </div>

      {/* Navigation */}
      <div className="px-2 py-3">
        <Link
          to="/dashboard"
          className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
            isAnalytics ? "bg-blue-600/10 text-blue-400" : "hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200"
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          Analytics
        </Link>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
        <p className="px-3 text-[10px] font-semibold text-zinc-600 uppercase tracking-wider mb-2 mt-2">
          Recent Chats
        </p>
        {conversations.length === 0 ? (
          <p className="text-xs text-zinc-600 text-center py-4">No chats yet.</p>
        ) : (
          conversations.map((c) => (
            <div
              key={c._id}
              className={`group flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all ${
                activeId === c._id && !isAnalytics
                  ? "bg-zinc-800 text-white"
                  : "hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200"
              }`}
              onClick={() => onSelect(c._id)}
            >
              <MessageSquare className="w-4 h-4 shrink-0" />
              <span className="flex-1 text-sm truncate">{c.title}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm(`Delete "${c.title}"?`)) onDelete(c._id);
                }}
                className="opacity-0 group-hover:opacity-100 text-zinc-500 hover:text-red-400 transition-all p-1"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-zinc-800/50">
        <button
          onClick={onLogout}
          className="flex items-center gap-3 w-full text-sm text-zinc-400 hover:text-red-400 transition-colors px-2 py-2 rounded-lg hover:bg-zinc-900/50"
        >
          <LogOut className="w-4 h-4" />
          Log out
        </button>
      </div>
    </aside>
  );
}