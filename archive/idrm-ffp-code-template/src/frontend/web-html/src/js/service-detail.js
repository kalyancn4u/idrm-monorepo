/**
 * js/service-detail.js — one request's detail (pages/service-detail.html?id=…).
 *
 * Auth-gated. Loads GET /services/{id}, renders the details + status badge +
 * timeline + a location mini-map, and shows the requestor's actions based on
 * status: Cancel (SUBMITTED/APPROVED), Confirm & rate (COMPLETED), Dispute
 * (IN_PROGRESS/COMPLETED). Action buttons only appear for the owner; the backend
 * enforces ownership + valid transitions regardless.
 *
 * (Provider/DM actions live on the provider + admin pages — F6 / React SPA.)
 */
import { getUser } from "./api/client.js";
import { cancelService, disputeService, getService, verifyService } from "./api/services.js";
import { requireAuth } from "./auth-guard.js";
import { escapeHtml, formatDateTime, mountAppHeader, priorityBadge, statusBadge } from "./ui.js";

const L = window.L; // Leaflet global (CDN <script> in <head>)
const id = new URLSearchParams(location.search).get("id");

if (requireAuth()) {
  mountAppHeader("my");
  if (!id) renderError("No request id in the URL.");
  else load();
}

async function load() {
  try {
    render(await getService(id));
  } catch (err) {
    renderError(err.status === 404 ? "Request not found." : err.message || "Couldn't load this request.");
  }
}

function renderError(message) {
  document.getElementById("detail").innerHTML = `<p class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 ring-1 ring-red-500/40">${escapeHtml(message)}</p>`;
  document.getElementById("actions").innerHTML = "";
}

function render(s) {
  const coords = s.location && s.location.coordinates; // [lon, lat]
  const stars = s.rating ? "★".repeat(s.rating) + "☆".repeat(5 - s.rating) : "";

  document.getElementById("detail").innerHTML = `
    <div class="flex flex-wrap items-center gap-2">
      <h1 class="mr-1 text-2xl font-bold text-slate-900">${escapeHtml(s.service_type)} request</h1>
      ${priorityBadge(s.priority)} ${statusBadge(s.status)}
    </div>
    <p class="mt-3 text-base text-slate-700">${escapeHtml(s.description)}</p>

    <dl class="mt-4 grid grid-cols-2 gap-3 text-sm">
      <div><dt class="text-slate-500">People affected</dt><dd class="font-medium text-slate-900">${escapeHtml(s.num_people_affected)}</dd></div>
      <div><dt class="text-slate-500">Privacy</dt><dd class="font-medium text-slate-900">${escapeHtml(s.privacy_level)}</dd></div>
      <div class="col-span-2"><dt class="text-slate-500">Address</dt><dd class="font-medium text-slate-900">${escapeHtml(s.address || "—")}</dd></div>
      ${s.contact_phone ? `<div class="col-span-2"><dt class="text-slate-500">Contact</dt><dd class="font-medium text-slate-900">${escapeHtml(s.contact_phone)}</dd></div>` : ""}
    </dl>

    <div id="map" class="mt-4 h-56 w-full overflow-hidden rounded-xl border border-slate-200"></div>

    <h2 class="mt-6 text-lg font-semibold text-slate-900">Timeline</h2>
    <ul class="mt-2 space-y-1 text-sm text-slate-600">
      <li>Created: ${formatDateTime(s.created_at)}</li>
      <li>Accepted: ${formatDateTime(s.accepted_at)}</li>
      <li>Completed: ${formatDateTime(s.completed_at)}</li>
      <li>Verified: ${formatDateTime(s.verified_at)}</li>
    </ul>

    ${s.provider ? `
      <div class="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
        <div class="text-sm font-semibold text-slate-900">Assigned provider</div>
        <div class="text-sm text-slate-700">${escapeHtml(s.provider.name)}${s.provider.contact_phone ? " · " + escapeHtml(s.provider.contact_phone) : ""}</div>
      </div>` : ""}

    ${s.rating ? `<p class="mt-4 text-sm text-slate-700">Your rating: <span class="text-amber-500">${stars}</span>${s.feedback ? " — " + escapeHtml(s.feedback) : ""}</p>` : ""}
  `;

  // Location mini-map.
  if (L && coords && coords.length === 2) {
    const [lon, lat] = coords;
    const map = L.map("map").setView([lat, lon], 14);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "© OpenStreetMap contributors",
    }).addTo(map);
    L.marker([lat, lon]).addTo(map);
  }

  renderActions(s);
}

function renderActions(s) {
  const box = document.getElementById("actions");
  const me = getUser();
  // The requestor brief is present only when the viewer may see it — for the owner it is.
  const isOwner = !!(me && s.requestor && s.requestor.user_id === me.id);
  if (!isOwner) {
    box.innerHTML = "";
    return;
  }

  const buttons = [];
  if (["SUBMITTED", "APPROVED"].includes(s.status)) buttons.push(btn("cancel", "Cancel request"));
  if (s.status === "COMPLETED") {
    buttons.push(`<button data-action="verify" class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700">Confirm &amp; rate</button>`);
  }
  if (["IN_PROGRESS", "COMPLETED"].includes(s.status)) buttons.push(btn("dispute", "Raise a dispute"));

  box.innerHTML = buttons.join("");
  box.querySelectorAll("[data-action]").forEach((b) => b.addEventListener("click", () => handleAction(b.dataset.action, s)));
}

function btn(action, label) {
  return `<button data-action="${action}" class="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100">${label}</button>`;
}

async function handleAction(name, s) {
  try {
    if (name === "cancel") {
      if (!confirm("Cancel this request?")) return;
      await cancelService(s.service_id, "Cancelled by requestor");
    } else if (name === "dispute") {
      const reason = prompt("What's the problem? (a short reason)");
      if (!reason) return;
      await disputeService(s.service_id, reason);
    } else if (name === "verify") {
      const rating = Number(prompt("Rate the service 1–5:", "5"));
      if (!(rating >= 1 && rating <= 5)) {
        alert("Please enter a rating from 1 to 5.");
        return;
      }
      const feedback = prompt("Optional feedback:") || null;
      await verifyService(s.service_id, rating, feedback);
    }
    load(); // refresh the detail after a successful action
  } catch (err) {
    alert(`Action failed: ${err.message}`);
  }
}
