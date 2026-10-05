/**
 * Login — credential form for coordinators/admins.
 * On success it routes to wherever the guard sent the user from (default "/").
 */
import { useState, type FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../store/auth";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation() as { state?: { from?: string } };

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(email, password);
      navigate(location.state?.from ?? "/", { replace: true });
    } catch (err) {
      setError((err as Error).message || "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-6 text-center">
          <span className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-600 text-white text-lg font-bold">
            ID
          </span>
          <h1 className="mt-3 text-xl font-semibold text-slate-900">IDRM Admin</h1>
          <p className="text-sm text-slate-500">Sign in to the coordination console</p>
        </div>

        <form
          onSubmit={onSubmit}
          className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 space-y-4"
        >
          {error && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none"
              autoComplete="username"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none"
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            disabled={busy}
            className="w-full rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
          >
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
