/**
 * ProtectedRoute — gate for authenticated routes.
 * Renders children when a session exists, otherwise redirects to /login.
 */
import type { ReactElement } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../store/auth";

export default function ProtectedRoute({ children }: { children: ReactElement }) {
  const isAuthenticated = useAuth((s) => s.isAuthenticated);
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}
