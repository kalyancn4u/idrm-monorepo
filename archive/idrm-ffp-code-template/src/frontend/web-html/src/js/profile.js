/**
 * js/profile.js — view + edit your own profile (pages/profile.html).
 *
 * Auth-gated. Loads GET /users/me, lets the user change their name, phone, and
 * language, and saves via POST /users/me ({ full_name, phone?, preferences }).
 * Email and role are read-only (role changes go through an ADMIN).
 */
import { getMe, updateMe } from "./api/client.js";
import { requireAuth } from "./auth-guard.js";
import { mountAppHeader } from "./ui.js";

const PHONE_RE = /^\+[1-9]\d{1,14}$/; // E.164

if (requireAuth()) {
  mountAppHeader("profile");
  init();
}

function message(text, ok) {
  const box = document.getElementById("form-msg");
  box.textContent = text;
  box.className = `mt-4 rounded-lg px-3 py-2 text-sm ${
    ok ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-500/40" : "bg-red-50 text-red-700 ring-1 ring-red-500/40"
  }`;
}

async function init() {
  const form = document.getElementById("profile-form");
  try {
    const user = await getMe();
    form.full_name.value = user.full_name || "";
    form.phone.value = user.phone || "";
    form.language.value = user.preferences?.language || "en";
    document.getElementById("email").textContent = user.email;
    document.getElementById("role").textContent = user.role;
  } catch (err) {
    message(`Couldn't load your profile (${err.message}).`, false);
  }
  form.addEventListener("submit", onSubmit);
}

async function onSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const fullName = form.full_name.value.trim();
  const phone = form.phone.value.trim();

  if (fullName.length < 2) return message("Please enter your full name.", false);
  if (phone && !PHONE_RE.test(phone)) {
    return message("Phone must be international format, e.g. +919876543210.", false);
  }

  // `preferences` is merged server-side, so sending just `language` is safe.
  const payload = { full_name: fullName, preferences: { language: form.language.value } };
  if (phone) payload.phone = phone;

  const saveBtn = document.getElementById("save-btn");
  saveBtn.disabled = true;
  saveBtn.textContent = "Saving…";
  try {
    await updateMe(payload);
    message("Profile saved.", true);
  } catch (err) {
    message(err.status === 409 ? "That phone is already in use." : err.message || "Couldn't save.", false);
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = "Save changes";
  }
}
