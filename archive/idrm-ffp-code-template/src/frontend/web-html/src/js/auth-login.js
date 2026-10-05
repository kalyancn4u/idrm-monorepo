/**
 * js/auth-login.js — behavior for the login page (pages/login.html).
 *
 * Validates the form, calls the API client to sign in (which stores the session),
 * then redirects to wherever the user was headed (`?next=`) or the dashboard.
 */
import { login } from "./api/client.js";
import { redirectIfAuthed } from "./auth-guard.js";

const DASHBOARD_URL = "/src/pages/dashboard.html";

redirectIfAuthed(); // already signed in? skip the form.

const form = document.getElementById("login-form");
const errorBox = document.getElementById("form-error");
const submitBtn = document.getElementById("submit-btn");

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.classList.add("hidden");

  const email = form.email.value.trim();
  const password = form.password.value;
  if (!email || !password) {
    showError("Email and password are required.");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Signing in…";
  try {
    await login(email, password);
    const next = new URLSearchParams(location.search).get("next");
    location.replace(next || DASHBOARD_URL);
  } catch (err) {
    showError(err.status === 401 ? "Incorrect email or password." : err.message || "Sign-in failed.");
    submitBtn.disabled = false;
    submitBtn.textContent = "Sign in";
  }
});
