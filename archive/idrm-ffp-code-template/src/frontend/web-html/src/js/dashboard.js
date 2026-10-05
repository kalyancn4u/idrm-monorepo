/**
 * js/dashboard.js — the citizen dashboard (pages/dashboard.html).
 *
 * Auth-gated. Greets the user (GET /users/me), shows their request count, and lists
 * their five most recent requests (GET /services?mine=true). Quick-action cards are
 * plain links in the HTML.
 */
import { getMe } from "./api/client.js";
import { listServices } from "./api/services.js";
import { requireAuth } from "./auth-guard.js";
import { escapeHtml, formatDateTime, mountAppHeader, priorityBadge, statusBadge } from "./ui.js";

if (requireAuth()) {
  mountAppHeader("dashboard");
  loadGreeting();
  loadRecent();
}

async function loadGreeting() {
  try {
    const user = await getMe();
    document.getElementById("greeting").textContent = `Welcome, ${user.full_name}`;
  } catch {
    /* keep the default greeting if /users/me fails */
  }
}

async function loadRecent() {
  const recent = document.getElementById("recent");
  const count = document.getElementById("request-count");
  try {
    const { data } = await listServices({ mine: true, per_page: 5 });
    count.textContent = String(data.total);
    recent.innerHTML = data.items.length
      ? data.items.map(card).join("")
      : `<p class="text-sm text-slate-500">No requests yet. <a href="/src/pages/create-service.html" class="text-emerald-600 hover:underline">Create one</a>.</p>`;
  } catch (err) {
    count.textContent = "—";
    recent.innerHTML = `<p class="text-sm text-red-600">Couldn't load your requests (${escapeHtml(err.message)}).</p>`;
  }
}

/** One request as a clickable card. `service_type` is escaped; the badges are trusted HTML. */
function card(s) {
  return `
    <a href="/src/pages/service-detail.html?id=${encodeURIComponent(s.service_id)}"
       class="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 hover:border-emerald-300 hover:shadow-sm">
      <div class="min-w-0">
        <div class="font-medium text-slate-900">${escapeHtml(s.service_type)} ${priorityBadge(s.priority)}</div>
        <div class="mt-1 truncate text-xs text-slate-500">${escapeHtml(s.address || "No address")} · ${formatDateTime(s.created_at)}</div>
      </div>
      ${statusBadge(s.status)}
    </a>`;
}
