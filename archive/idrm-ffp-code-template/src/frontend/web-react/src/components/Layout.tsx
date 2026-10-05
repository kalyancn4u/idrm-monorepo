/**
 * Layout — the admin shell shared by every authenticated page.
 * Fixed sidebar (brand + nav) on the left, a top bar with the signed-in user
 * and a sign-out button, and an <Outlet /> for the active route.
 */
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../store/auth";

/** Sidebar links. `end` keeps "/" from matching every nested route. */
const NAV = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/requests", label: "Approval queue", end: false },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleSignOut() {
    await logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="min-h-screen flex bg-slate-50">
      {/* Sidebar */}
      <aside className="w-60 shrink-0 bg-slate-900 text-slate-300 flex flex-col">
        <div className="h-16 flex items-center gap-2 px-5 border-b border-slate-800">
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-600 text-white font-bold">
            ID
          </span>
          <span className="font-semibold text-white">IDRM Admin</span>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive ? "bg-emerald-600 text-white" : "text-slate-300 hover:bg-slate-800 hover:text-white"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-5 py-4 border-t border-slate-800 text-xs text-slate-500">
          IDRM v3 · MVP
        </div>
      </aside>

      {/* Main column */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-end gap-4 px-6">
          <div className="text-right leading-tight">
            <div className="text-sm font-medium text-slate-800">{user?.full_name ?? "—"}</div>
            <div className="text-xs text-slate-500">{user?.role ?? ""}</div>
          </div>
          <button
            type="button"
            onClick={handleSignOut}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
          >
            Sign out
          </button>
        </header>

        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
