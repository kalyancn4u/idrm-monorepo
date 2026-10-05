/**
 * js/my-services.js — the citizen's request list (pages/my-services.html).
 *
 * Auth-gated. Lists the signed-in user's requests (GET /services?mine=true) with a
 * status filter + pagination, and a quick Cancel on requests that are still
 * cancellable (SUBMITTED / APPROVED).
 */
import { cancelService, listServices } from "./api/services.js";
import { requireAuth } from "./auth-guard.js";
import { escapeHtml, formatDateTime, mountAppHeader, priorityBadge, statusBadge } from "./ui.js";

const CANCELLABLE = new Set(["SUBMITTED", "APPROVED"]);
let page = 1;
let statusFilter = "";

if (requireAuth()) {
  mountAppHeader("my");
  document.getElementById("status-filter")?.addEventListener("change", (event) => {
    statusFilter = event.target.value;
    page = 1;
    load();
  });
  load();
}

async function load() {
  const list = document.getElementById("list");
  list.innerHTML = `<p class="text-sm text-slate-500">Loading…</p>`;
  try {
    const { data } = await listServices({ mine: true, status: statusFilter, page, per_page: 20 });
    list.innerHTML = data.items.length
      ? data.items.map(row).join("")
      : `<p class="text-sm text-slate-500">No requests found.</p>`;
    wireCancelButtons();
    renderPager(data);
  } catch (err) {
    list.innerHTML = `<p class="text-sm text-red-600">Couldn't load your requests (${escapeHtml(err.message)}).</p>`;
  }
}

function row(s) {
  const cancelBtn = CANCELLABLE.has(s.status)
    ? `<button data-cancel="${escapeHtml(s.service_id)}" class="rounded-lg border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100">Cancel</button>`
    : "";
  return `
    <div class="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-4">
      <a href="/src/pages/service-detail.html?id=${encodeURIComponent(s.service_id)}" class="min-w-0">
        <div class="font-medium text-slate-900">${escapeHtml(s.service_type)} ${priorityBadge(s.priority)}</div>
        <div class="mt-1 truncate text-xs text-slate-500">${escapeHtml(s.address || "No address")} · ${formatDateTime(s.created_at)}</div>
      </a>
      <div class="flex shrink-0 items-center gap-3">${statusBadge(s.status)}${cancelBtn}</div>
    </div>`;
}

function wireCancelButtons() {
  document.querySelectorAll("[data-cancel]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.getAttribute("data-cancel");
      if (!confirm("Cancel this request?")) return;
      btn.disabled = true;
      try {
        await cancelService(id, "Cancelled by requestor");
        load();
      } catch (err) {
        alert(`Couldn't cancel: ${err.message}`);
        btn.disabled = false;
      }
    });
  });
}

function renderPager(data) {
  const pager = document.getElementById("pager");
  if (!pager) return;
  if (data.pages <= 1) {
    pager.innerHTML = "";
    return;
  }
  pager.innerHTML = `
    <button id="prev" ${data.page <= 1 ? "disabled" : ""} class="rounded-lg border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50">Prev</button>
    <span class="text-sm text-slate-500">Page ${data.page} of ${data.pages}</span>
    <button id="next" ${data.page >= data.pages ? "disabled" : ""} class="rounded-lg border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50">Next</button>`;
  document.getElementById("prev")?.addEventListener("click", () => {
    page = Math.max(1, page - 1);
    load();
  });
  document.getElementById("next")?.addEventListener("click", () => {
    page += 1;
    load();
  });
}
