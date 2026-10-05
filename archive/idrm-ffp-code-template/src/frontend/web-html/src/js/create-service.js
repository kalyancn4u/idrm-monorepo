/**
 * js/create-service.js — the "Request help" form (pages/create-service.html).
 *
 * Auth-gated. Lets the citizen pick a location on a Leaflet map (or "Use my
 * location"), fill in the request, and POST it to /services. On success it goes to
 * the new request's detail page.
 *
 * GeoJSON note: the API wants `location.coordinates` as [longitude, latitude]
 * (lon first) — the opposite of Leaflet's [lat, lng].
 */
import { getMe } from "./api/client.js";
import { createService } from "./api/services.js";
import { requireAuth } from "./auth-guard.js";
import { mountAppHeader } from "./ui.js";

const HYDERABAD = [17.385, 78.4867]; // [lat, lng] — default map centre (pilot region)
const L = window.L; // Leaflet global, from the CDN <script> in the page <head>

let map;
let marker;
let selected = null; // { lat, lng } the user chose

if (requireAuth()) {
  mountAppHeader("");
  initMap();
  prefillPhone();
  document.getElementById("create-form").addEventListener("submit", onSubmit);
  document.getElementById("locate-btn").addEventListener("click", useMyLocation);
}

function showError(message) {
  const box = document.getElementById("form-error");
  box.textContent = message;
  box.classList.remove("hidden");
}

function setLocation(lat, lng) {
  selected = { lat, lng };
  if (marker) marker.setLatLng([lat, lng]);
  else if (map) marker = L.marker([lat, lng]).addTo(map);
  document.getElementById("coords").textContent = `📍 ${lat.toFixed(5)}, ${lng.toFixed(5)}`;
}

function initMap() {
  const el = document.getElementById("map");
  if (!L) {
    el.innerHTML = '<p class="p-4 text-sm text-red-600">Map couldn\'t load — you can still submit by typing an address.</p>';
    return;
  }
  map = L.map("map").setView(HYDERABAD, 12);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "© OpenStreetMap contributors",
  }).addTo(map);
  map.on("click", (e) => setLocation(e.latlng.lat, e.latlng.lng));
}

function useMyLocation() {
  if (!navigator.geolocation) {
    showError("Geolocation isn't available — tap the map to set the location.");
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const { latitude, longitude } = pos.coords;
      if (map) map.setView([latitude, longitude], 15);
      setLocation(latitude, longitude);
    },
    () => showError("Couldn't get your location — tap the map to set it instead."),
  );
}

async function prefillPhone() {
  try {
    const user = await getMe();
    if (user.phone) document.getElementById("contact_phone").value = user.phone;
  } catch {
    /* optional pre-fill; ignore failures */
  }
}

async function onSubmit(event) {
  event.preventDefault();
  document.getElementById("form-error").classList.add("hidden");
  const form = event.target;

  if (!selected) return showError("Set the location — tap the map or use “Use my location”.");
  const description = form.description.value.trim();
  if (description.length < 10) return showError("Please describe the situation (at least 10 characters).");

  const payload = {
    service_type: form.service_type.value,
    priority: form.priority.value,
    description,
    location: { type: "Point", coordinates: [selected.lng, selected.lat] }, // [lon, lat]
    address: form.address.value.trim() || null,
    num_people_affected: Number(form.num_people_affected.value) || 1,
    privacy_level: form.privacy_level.value,
    contact_phone: form.contact_phone.value.trim() || null,
  };

  const submitBtn = document.getElementById("submit-btn");
  submitBtn.disabled = true;
  submitBtn.textContent = "Submitting…";
  try {
    const created = await createService(payload);
    location.replace(`/src/pages/service-detail.html?id=${encodeURIComponent(created.service_id)}`);
  } catch (err) {
    showError(err.status === 422 ? "Please check the form and try again." : err.message || "Couldn't submit your request.");
    submitBtn.disabled = false;
    submitBtn.textContent = "Submit request";
  }
}
