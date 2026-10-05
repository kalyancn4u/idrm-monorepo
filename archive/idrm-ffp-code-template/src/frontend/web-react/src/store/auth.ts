/**
 * auth.ts — global auth state (Zustand).
 *
 * Seeds from sessionStorage so a page reload keeps the session. Components read
 * `isAuthenticated` (route guarding) and `user` (role-aware UI), and call
 * `login` / `logout`. Token persistence itself lives in lib/api.ts.
 */
import { create } from "zustand";
import { getMe, login as apiLogin, logout as apiLogout, tokens, type User } from "../lib/api";

interface AuthState {
  /** The logged-in user, or null when signed out. */
  user: User | null;
  /** True when an access token is present. */
  isAuthenticated: boolean;
  /** Authenticate and store the user; throws on bad credentials. */
  login: (email: string, password: string) => Promise<void>;
  /** Clear the session (server + local) and reset state. */
  logout: () => Promise<void>;
  /** Refresh the cached user from GET /users/me (no-op on failure). */
  loadUser: () => Promise<void>;
}

/** Read the user cached at login (survives reloads within the tab). */
function cachedUser(): User | null {
  try {
    const raw = sessionStorage.getItem("user");
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}

export const useAuth = create<AuthState>((set) => ({
  user: cachedUser(),
  isAuthenticated: Boolean(tokens.access()),

  login: async (email, password) => {
    const user = await apiLogin(email, password);
    set({ user, isAuthenticated: true });
  },

  logout: async () => {
    await apiLogout();
    set({ user: null, isAuthenticated: false });
  },

  loadUser: async () => {
    try {
      const user = await getMe();
      sessionStorage.setItem("user", JSON.stringify(user));
      set({ user });
    } catch {
      /* token may be invalid; route guard handles redirect */
    }
  },
}));
