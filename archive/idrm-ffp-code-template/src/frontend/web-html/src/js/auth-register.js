/**
 * js/auth-register.js — behavior for the registration page (pages/register.html).
 *
 * Validates the form, creates the account, then auto-signs-in and goes to the
 * dashboard. Self-service roles are limited to CITIZEN / PROVIDER / VOLUNTEER
 * (the backend enforces this too — we just keep the UI honest).
 */
import { login, register } from "./api/client.js";
import { redirectIfAuthed } from "./auth-guard.js";

const DASHBOARD_URL = "/src/pages/dashboard.html";
const PHONE_RE = /^\+[1-9]\d{1,14}$/; // E.164, e.g. +919876543210

redirectIfAuthed();

const form = document.getElementById("register-form");
const errorBox = document.getElementById("form-error");
const submitBtn = document.getElementById("submit-btn");

// Preselect the role if the landing linked here with ?role=PROVIDER (etc.).
const roleParam = new URLSearchParams(location.search).get("role");
if (roleParam && form?.role && ["CITIZEN", "PROVIDER", "VOLUNTEER"].includes(roleParam)) {
  form.role.value = roleParam;
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.classList.add("hidden");

  const payload = {
    full_name: form.full_name.value.trim(),
    email: form.email.value.trim(),
    password: form.password.value,
    role: form.role.value,
    language_preference: form.language_preference.value,
  };
  const phone = form.phone.value.trim();
  if (phone) payload.phone = phone;

  // Client-side validation (the backend validates again — this is just fast feedback).
  if (payload.full_name.length < 2) return showError("Please enter your full name.");
  if (payload.password.length < 8) return showError("Password must be at least 8 characters.");
  if (phone && !PHONE_RE.test(phone)) {
    return showError("Phone must be international format, e.g. +919876543210.");
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Creating account…";
  try {
    await register(payload);
    await login(payload.email, payload.password); // auto sign-in after registering
    location.replace(DASHBOARD_URL);
  } catch (err) {
    if (err.status === 409) showError("That email or phone is already registered.");
    else if (err.status === 403) showError("That role can't be self-assigned.");
    else if (err.status === 422) showError("Please check your details and try again.");
    else showError(err.message || "Registration failed.");
    submitBtn.disabled = false;
    submitBtn.textContent = "Create account";
  }
});
