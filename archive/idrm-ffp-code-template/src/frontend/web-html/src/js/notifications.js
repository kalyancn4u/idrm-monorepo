/**
 * js/notifications.js — the notifications list (pages/notifications.html).
 *
 * Auth-gated. Lists the user's notifications (GET /notifications), highlights unread
 * ones, lets them be marked read (POST /notifications/{id}/read), and links each one
 * to its related request (when `related_service_id` is present).
 */
import { listNotifications, markNotificationRead } from "./api/notifications.js";
import { requireAuth } from "./auth-guard.js";
import { escapeHtml, formatDateTime, mountAppHeader } from "./ui.js";

if (requireAuth()) {
  mountAppHeader("notifications");
  load();
}

async function load() {
  const list = document.getElementById("list");
  list.innerHTML = `<p class="text-sm text-slate-500">Loading…</p>`;
  try {
    const { data } = await listNotifications();
    document.getElementById("unread").textContent = String(data.unread_count);
    list.innerHTML = data.items.length
      ? data.items.map(row).join("")
      : `<p class="text-sm text-slate-500">No notifications yet.</p>`;
    wireMarkButtons();
  } catch (err) {
    list.innerHTML = `<p class="text-sm text-red-600">Couldn't load notifications (${escapeHtml(err.message)}).</p>`;
  }
}

function row(n) {
  const unreadCls = n.read ? "border-slate-200 bg-white" : "border-emerald-200 bg-emerald-50/60";
  const link = n.related_service_id ? `/src/pages/service-detail.html?id=${encodeURIComponent(n.related_service_id)}` : null;
  const title = escapeHtml(n.title || n.type);
  const titleHtml = link ? `<a href="${link}" class="hover:underline">${title}</a>` : title;
  const markBtn = n.read
    ? ""
    : `<button data-read="${escapeHtml(n.id)}" class="shrink-0 rounded-lg border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100">Mark read</button>`;
  return `
    <div class="flex items-start justify-between gap-3 rounded-xl border ${unreadCls} p-4">
      <div class="min-w-0">
        <div class="font-medium text-slate-900">${titleHtml}</div>
        <div class="mt-1 text-sm text-slate-600">${escapeHtml(n.message)}</div>
        <div class="mt-1 text-xs text-slate-400">${escapeHtml(n.type)} · ${formatDateTime(n.created_at)}</div>
      </div>
      ${markBtn}
    </div>`;
}

function wireMarkButtons() {
  document.querySelectorAll("[data-read]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      btn.disabled = true;
      try {
        await markNotificationRead(btn.getAttribute("data-read"));
        load(); // refresh list + unread count
      } catch (err) {
        alert(`Couldn't mark read: ${err.message}`);
        btn.disabled = false;
      }
    });
  });
}
