/**
 * Requests — the approval queue (the distinctly-admin DM_AUTHORITY capability).
 *
 * Lists SUBMITTED requests (GET /services?status=SUBMITTED) and lets a
 * DM_AUTHORITY / ADMIN approve (POST /services/{id}/approve) or reject
 * (POST /services/{id}/reject). The backend enforces the role — a non-authorised
 * account simply gets a 403 surfaced as an inline error. After each action the
 * list is invalidated so the row drops out of the queue.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  approveService,
  listServices,
  rejectService,
  type Paginated,
  type Priority,
  type ServiceRequest,
} from "../lib/api";

/** Tailwind classes for a priority pill (see instructions_ui_v3.md). */
const PRIORITY_CLASS: Record<Priority, string> = {
  CRITICAL: "bg-red-100 text-red-800",
  HIGH: "bg-orange-100 text-orange-800",
  MEDIUM: "bg-amber-100 text-amber-800",
  LOW: "bg-slate-100 text-slate-700",
};

/** Short, locale-aware timestamp. */
function formatDateTime(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString();
}

export default function Requests() {
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState<string | null>(null);

  // The pending approval queue.
  const { data, isLoading, isError, error } = useQuery<Paginated<ServiceRequest>>({
    queryKey: ["services", "SUBMITTED"],
    queryFn: () => listServices({ status: "SUBMITTED", per_page: 100 }),
  });

  // Approve / reject share invalidation + error handling.
  const onSettledRefresh = () => queryClient.invalidateQueries({ queryKey: ["services", "SUBMITTED"] });

  const approve = useMutation({
    mutationFn: (id: string) => approveService(id, "Approved for dispatch"),
    onError: (e) => setActionError((e as Error).message),
    onSuccess: () => {
      setActionError(null);
      onSettledRefresh();
    },
  });

  const reject = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) => rejectService(id, reason),
    onError: (e) => setActionError((e as Error).message),
    onSuccess: () => {
      setActionError(null);
      onSettledRefresh();
    },
  });

  function handleReject(id: string) {
    const reason = window.prompt("Reason for rejection?");
    if (reason && reason.trim()) reject.mutate({ id, reason: reason.trim() });
  }

  const busyId = approve.isPending
    ? approve.variables
    : reject.isPending
      ? reject.variables?.id
      : undefined;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-900">Approval queue</h1>
        <span className="text-sm text-slate-500">
          {data ? `${data.data.total} pending` : ""}
        </span>
      </div>

      {actionError && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {actionError}
        </div>
      )}

      {isLoading && <p className="text-slate-500">Loading queue…</p>}

      {isError && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          Couldn’t load the queue: {(error as Error)?.message ?? "unknown error"}
        </div>
      )}

      {data && data.data.items.length === 0 && (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">
          Nothing awaiting approval. 🎉
        </div>
      )}

      {data && data.data.items.length > 0 && (
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">Description</th>
                <th className="px-4 py-3">Location</th>
                <th className="px-4 py-3">Submitted</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.data.items.map((req) => {
                const isRowBusy = busyId === req.service_id;
                return (
                  <tr key={req.service_id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium text-slate-800">{req.service_type}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-semibold ${PRIORITY_CLASS[req.priority]}`}>
                        {req.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3 max-w-xs truncate text-slate-600" title={req.description}>
                      {req.description}
                    </td>
                    <td className="px-4 py-3 text-slate-600">{req.address ?? "—"}</td>
                    <td className="px-4 py-3 text-slate-500">{formatDateTime(req.created_at)}</td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          disabled={isRowBusy}
                          onClick={() => approve.mutate(req.service_id)}
                          className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
                        >
                          Approve
                        </button>
                        <button
                          type="button"
                          disabled={isRowBusy}
                          onClick={() => handleReject(req.service_id)}
                          className="rounded-lg border border-red-300 px-3 py-1.5 text-xs font-semibold text-red-700 hover:bg-red-50 disabled:opacity-50"
                        >
                          Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
