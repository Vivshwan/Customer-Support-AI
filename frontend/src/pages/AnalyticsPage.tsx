import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchAnalytics } from "../api/client";
import type { AnalyticsSummary } from "../types";

const AGENT_COLORS: Record<string, string> = {
  billing: "#10b981",
  technical: "#3b82f6",
  product: "#a855f7",
  complaint: "#f97316",
  faq: "#6b7280",
};

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="bg-white rounded-xl shadow p-4">
      <p className="text-xs uppercase tracking-wide text-gray-500">{label}</p>
      <p className="text-3xl font-semibold text-gray-900 mt-1">{value}</p>
    </div>
  );
}

export function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics()
      .then(setData)
      .catch((e) =>
        setError(e?.response?.data?.detail || "Failed to load analytics.")
      )
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-500">
        Loading analytics...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-red-600 gap-3">
        <p>⚠️ {error ?? "No data."}</p>
        <Link to="/" className="text-blue-600 hover:underline text-sm">
          ← Back to chat
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">
              Analytics Dashboard
            </h1>
            <p className="text-sm text-gray-500">
              Usage summary for your account
            </p>
          </div>
          <Link
            to="/"
            className="text-sm bg-white border border-gray-300 rounded-lg px-3 py-2 hover:bg-gray-50 transition-colors"
          >
            ← Back to chat
          </Link>
        </div>

        {/* Stat cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="Conversations" value={data.totals.conversations} />
          <StatCard label="Messages" value={data.totals.messages} />
          <StatCard label="Agent calls" value={data.totals.agent_calls} />
          <StatCard
            label="AI responses"
            value={data.totals.assistant_messages}
          />
        </div>

        {/* Charts row */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Agent usage */}
          <div className="bg-white rounded-xl shadow p-5">
            <h2 className="font-semibold text-gray-900 mb-4">Agent usage</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={data.agents}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="agent" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {data.agents.map((a) => (
                    <Cell
                      key={a.agent}
                      fill={AGENT_COLORS[a.agent] ?? "#6b7280"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Daily messages */}
          <div className="bg-white rounded-xl shadow p-5">
            <h2 className="font-semibold text-gray-900 mb-4">
              Messages (last 7 days)
            </h2>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={data.daily}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(d: string) => d.slice(5)}
                />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent conversations */}
        <div className="bg-white rounded-xl shadow p-5">
          <h2 className="font-semibold text-gray-900 mb-4">
            Recent conversations
          </h2>
          {data.recent.length === 0 ? (
            <p className="text-sm text-gray-500">No conversations yet.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 font-medium">Title</th>
                  <th className="pb-2 font-medium">Messages</th>
                  <th className="pb-2 font-medium">Last updated</th>
                </tr>
              </thead>
              <tbody>
                {data.recent.map((c) => (
                  <tr key={c.id} className="border-b last:border-0">
                    <td className="py-2 text-gray-900">{c.title}</td>
                    <td className="py-2 text-gray-600">{c.message_count}</td>
                    <td className="py-2 text-gray-500 text-xs">
                      {new Date(c.updated_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}