/**
 * js/ui.js — small shared UI helpers for the app pages.
 *
 * Status/priority badge classes come straight from instructions_ui_v3.md (the
 * canonical Slate+Emerald rulebook). `mountAppHeader` injects the signed-in nav and
 * wires Sign-out. `escapeHtml` MUST be used on any user-supplied text before it's
 * placed into innerHTML (descriptions, addresses, names) to avoid HTML injection.
 */
import { getUser, logout } from "./api/client.js";

// Status → Tailwind classes (instructions_ui_v3.md §status badges).
const STATUS_CLASSES = {
  SUBMITTED: "bg-slate-100 text-slate-700",
  APPROVED: "bg-blue-50 text-blue-700",
  ACCEPTED: "bg-indigo-50 text-indigo-700",
  IN_PROGRESS: "bg-amber-50 text-amber-700",
  COMPLETED: "bg-emerald-50 text-emerald-700",
  VERIFIED: "bg-emerald-100 text-emerald-800",
  REJECTED: "bg-red-50 text-red-700",
  DISPUTED: "bg-white text-red-700 ring-1 ring-red-500",
  CANCELLED: "bg-slate-100 text-slate-600",
  EXPIRED: "bg-slate-100 text-slate-500",
};

// Priority → Tailwind classes (instructions_ui_v3.md §priority badges; FS map colours).
const PRIORITY_CLASSES = {
  CRITICAL: "bg-red-50 text-red-700 ring-1 ring-red-500/40",
  HIGH: "bg-orange-50 text-orange-700 ring-1 ring-orange-500/40",
  MEDIUM: "bg-amber-50 text-amber-700 ring-1 ring-amber-500/40",
  LOW: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-500/40",
};

/** Escape text for safe insertion into innerHTML. */
export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function pill(text, classes) {
  return `<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${classes}">${escapeHtml(text)}</span>`;
}

/** A status badge `<span>` (e.g. statusBadge("IN_PROGRESS")). */
export const statusBadge = (status) =>
  pill(String(status).replace(/_/g, " "), STATUS_CLASSES[status] || "bg-slate-100 text-slate-700");

/** A priority badge `<span>` (e.g. priorityBadge("CRITICAL")). */
export const priorityBadge = (priority) =>
  pill(priority, PRIORITY_CLASSES[priority] || "bg-slate-100 text-slate-700");

/** Human-friendly local date-time (or "—" when missing). */
export function formatDateTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? String(iso) : d.toLocaleString();
}

/**
 * Inject the signed-in app header into `#app-header` and wire the Sign-out button.
 * @param {string} active  one of "dashboard" | "my" | "map" — highlights that link.
 */
export function mountAppHeader(active = "") {
  const host = document.getElementById("app-header");
  if (!host) return;
  const user = getUser();
  const link = (key, href, label) =>
    `<a href="${href}" class="text-sm font-medium ${
      active === key ? "text-emerald-700" : "text-slate-600 hover:text-emerald-700"
    }">${label}</a>`;

  host.innerHTML = `
    <div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
      <a href="/src/pages/dashboard.html" class="text-lg font-extrabold tracking-tight text-slate-900">IDRM</a>
      <nav class="flex items-center gap-4" aria-label="Primary">
        ${link("dashboard", "/src/pages/dashboard.html", "Dashboard")}
        ${link("my", "/src/pages/my-services.html", "My requests")}
        ${link("map", "/src/pages/map-view.html", "Map")}
        ${link("notifications", "/src/pages/notifications.html", "Notifications")}
        ${link("profile", "/src/pages/profile.html", "Profile")}
        ${["PROVIDER", "ADMIN"].includes(user?.role) ? link("provider", "/src/pages/provider.html", "Provider") : ""}
        <span class="hidden text-sm text-slate-400 sm:inline">${escapeHtml(user?.full_name ?? "")}</span>
        <button id="logout-btn" class="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-semibold text-slate-700 hover:bg-slate-100">Sign out</button>
      </nav>
    </div>`;

  document.getElementById("logout-btn")?.addEventListener("click", async () => {
    await logout();
    location.replace("/");
  });
}
