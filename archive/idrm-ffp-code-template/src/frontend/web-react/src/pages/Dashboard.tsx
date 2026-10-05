/**
 * Dashboard — operational analytics from GET /analytics/dashboard.
 * Headline stat cards + two Recharts bar charts (requests by service type and
 * by lifecycle status). Server state is fetched/cached via React Query.
 */
import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getDashboard, type DashboardData } from "../lib/api";

/** Bar colour per service type (emerald family + accents). */
const SERVICE_COLORS: Record<string, string> = {
  RESCUE: "#dc2626",
  MEDICAL: "#059669",
  FOOD: "#d97706",
  WATER: "#0891b2",
  SHELTER: "#7c3aed",
  OTHER: "#64748b",
};

/** Turn a `{ KEY: count }` map into Recharts' `[{ name, value }]` rows. */
function toChartData(map: Record<string, number>) {
  return Object.entries(map).map(([name, value]) => ({ name, value }));
}

/** A single headline metric card. */
function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold text-slate-900">{value}</div>
    </div>
  );
}

export default function Dashboard() {
  const { data, isLoading, isError, error } = useQuery<DashboardData>({
    queryKey: ["dashboard"],
    queryFn: getDashboard,
  });

  if (isLoading) {
    return <p className="text-slate-500">Loading analytics…</p>;
  }
  if (isError || !data) {
    return (
      <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
        Couldn’t load analytics: {(error as Error)?.message ?? "unknown error"}
      </div>
    );
  }

  const serviceData = toChartData(data.by_service_type);
  const statusData = toChartData(data.by_status);

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold text-slate-900">Dashboard</h1>

      {/* Headline metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total requests" value={data.total_requests} />
        <StatCard label="Active requests" value={data.active_requests} />
        <StatCard label="Avg response (min)" value={data.avg_response_time_min} />
        <StatCard label="Completion rate" value={`${Math.round(data.completion_rate * 100)}%`} />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <h2 className="mb-4 text-sm font-semibold text-slate-700">Requests by service type</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={serviceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {serviceData.map((entry) => (
                  <Cell key={entry.name} fill={SERVICE_COLORS[entry.name] ?? "#059669"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <h2 className="mb-4 text-sm font-semibold text-slate-700">Requests by status</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={statusData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-25} textAnchor="end" height={60} />
              <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#059669" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
