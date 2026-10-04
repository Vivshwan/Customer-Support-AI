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
  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-4 border-b border-gray-800">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center font-bold text-sm">
            TM
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold truncate">TechMart</p>
            <p className="text-[10px] text-gray-400 truncate">
              {userName ?? "Support AI"}
            </p>
          </div>
        </div>
        <button
          onClick={onNew}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm
                     rounded-lg py-2 font-medium transition-colors"
        >
          + New chat
        </button>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto py-2">
        {conversations.length === 0 ? (
          <p className="text-xs text-gray-500 text-center px-4 py-8">
            No conversations yet. Start a new chat.
          </p>
        ) : (
          conversations.map((c) => (
            <div
              key={c._id}
              className={`group flex items-center gap-2 px-3 py-2 mx-2 rounded-lg cursor-pointer transition-colors ${
                activeId === c._id
                  ? "bg-gray-700"
                  : "hover:bg-gray-800"
              }`}
              onClick={() => onSelect(c._id)}
            >
              <span className="flex-1 text-sm truncate">{c.title}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm(`Delete "${c.title}"?`)) onDelete(c._id);
                }}
                className="opacity-0 group-hover:opacity-100 text-gray-400
                           hover:text-red-400 text-xs transition-opacity"
                title="Delete"
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-gray-800">
        <button
          onClick={onLogout}
          className="w-full text-sm text-gray-400 hover:text-red-400 transition-colors text-left"
        >
          Logout
        </button>
      </div>
    </aside>
  );
}