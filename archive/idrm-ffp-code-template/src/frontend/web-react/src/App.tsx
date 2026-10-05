/**
 * App.tsx — route table.
 *
 * Public:    /login
 * Protected: /          → Dashboard (analytics)
 *            /requests  → approval queue (DM_AUTHORITY / ADMIN)
 * Everything else redirects to the dashboard (which itself guards to /login).
 */
import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Requests from "./pages/Requests";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      {/* Authenticated area — shares the admin shell (sidebar + header). */}
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/requests" element={<Requests />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
