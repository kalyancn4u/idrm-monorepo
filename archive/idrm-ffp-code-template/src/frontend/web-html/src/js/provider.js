/**
 * js/provider.js — the provider workspace (pages/provider.html).
 *
 * Auth-gated; intended for PROVIDER (or ADMIN) accounts. Two lists:
 *   • Available — APPROVED requests awaiting a provider (GET /services?status=APPROVED) → Accept.
 *   • My active — this org's ACCEPTED/IN_PROGRESS requests (GET /services?provider_id=<org>) → Start / Complete.
 *
 * Org gap: until accounts are linked to organizations, the provider pastes their
 * verified org's UUID (kept in localStorage). It's sent as `org_id` on Accept and
 * used to filter "my active". (See the M3 known gap in service_service.py.)
 */
import { getUser } from "./api/client.js";
import { acceptService, completeService, listServices, startService } from "./api/services.js";
import { requireAuth } from "./auth-guard.js";
import { escapeHtml, formatDateTime, mountAppHeader, priorityBadge, statusBadge } from "./ui.js";

const ORG_KEY = "idrm_org_id";
const getOrgId = () => localStorage.getItem(ORG_KEY) || "";

if (requireAuth()) {
  mountAppHeader("provider");
  start();
}

function start() {
  const user = getUser();
  if (user && !["PROVIDER", "ADMIN"].includes(user.role)) {
    document.getElementById("provider-root").innerHTML =
      `<p class="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-700 ring-1 ring-amber-500/40">This area is for provider accounts.</p>`;
    return;
  }
  document.getElementById("org-id").value = getOrgId();
  document.getElementById("save-org").addEventListener("click", () => {
    localStorage.setItem(ORG_KEY, document.getElementById("org-id").value.trim());
    refresh();
  });
  refresh();
}

function refresh() {
  loadAvailable();
  loadActive();
}

async function loadAvailable() {
  const el = document.getElementById("available");
  el.innerHTML = `<p class="text-sm text-slate-500">Loading…</p>`;
  try {
    const { data } = await listServices({ status: "APPROVED", per_page: 50 });
    el.innerHTML = data.items.length
      ? data.items.map(availableRow).join("")
      : `<p class="text-sm text-slate-500">No requests are awaiting a provider right now.</p>`;
    el.querySelectorAll("[data-accept]").forEach((b) => b.addEventListener("click", () => onAccept(b)));
  } catch (err) {
    el.innerHTML = `<p class="text-sm text-red-600">Couldn't load available requests (${escapeHtml(err.message)}).</p>`;
  }
}

async function loadActive() {
  const el = document.getElementById("active");
  const org = getOrgId();
  if (!org) {
    el.innerHTML = `<p class="text-sm text-slate-500">Set your Organization ID above to see your assignments.</p>`;
    return;
  }
  el.innerHTML = `<p class="text-sm text-slate-500">Loading…</p>`;
  try {
    const { data } = await listServices({ provider_id: org, per_page: 50 });
    el.innerHTML = data.items.length
      ? data.items.map(activeRow).join("")
      : `<p class="text-sm text-slate-500">No active assignments.</p>`;
    el.querySelectorAll("[data-start]").forEach((b) => b.addEventListener("click", () => runAction(startService(b.dataset.start), b)));
    el.querySelectorAll("[data-complete]").forEach((b) => b.addEventListener("click", () => runAction(completeService(b.dataset.complete), b)));
  } catch (err) {
    el.innerHTML = `<p class="text-sm text-red-600">Couldn't load your assignments (${escapeHtml(err.message)}).</p>`;
  }
}

function rowShell(s, right) {
  return `
    <div class="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-4">
      <a href="/src/pages/service-detail.html?id=${encodeURIComponent(s.service_id)}" class="min-w-0">
        <div class="font-medium text-slate-900">${escapeHtml(s.service_type)} ${priorityBadge(s.priority)}</div>
        <div class="mt-1 truncate text-xs text-slate-500">${escapeHtml(s.address || "No address")} · ${formatDateTime(s.created_at)}</div>
      </a>
      <div class="flex shrink-0 items-center gap-3">${right}</div>
    </div>`;
}

function availableRow(s) {
  const accept = `<button data-accept="${escapeHtml(s.service_id)}" class="rounded-lg bg-emerald-600 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-700">Accept</button>`;
  return rowShell(s, `${statusBadge(s.status)}${accept}`);
}

function activeRow(s) {
  let btn = "";
  if (s.status === "ACCEPTED") {
    btn = `<button data-start="${escapeHtml(s.service_id)}" class="rounded-lg border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100">Start</button>`;
  } else if (s.status === "IN_PROGRESS") {
    btn = `<button data-complete="${escapeHtml(s.service_id)}" class="rounded-lg bg-emerald-600 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-700">Complete</button>`;
  }
  return rowShell(s, `${statusBadge(s.status)}${btn}`);
}

async function onAccept(btn) {
  const org = getOrgId();
  if (!org) {
    alert("Set your Organization ID first (the box at the top).");
    return;
  }
  btn.disabled = true;
  try {
    await acceptService(btn.dataset.accept, org);
    refresh();
  } catch (err) {
    alert(`Couldn't accept: ${err.message}`);
    btn.disabled = false;
  }
}

async function runAction(promise, btn) {
  btn.disabled = true;
  try {
    await promise;
    refresh();
  } catch (err) {
    alert(`Action failed: ${err.message}`);
    btn.disabled = false;
  }
}
