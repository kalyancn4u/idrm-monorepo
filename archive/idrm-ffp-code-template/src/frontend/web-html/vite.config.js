/**
 * vite.config.js — dev server + build config for the HTML/Tailwind frontend.
 *
 * • Serves on :5173 with hot-reload (`bun run dev`).
 * • Proxies `/api` and `/ws` to the Bun gateway (:3000 / :3001) so the app uses
 *   RELATIVE URLs (`/api/v1/...`) and avoids CORS in dev — the same shape NGINX
 *   serves in production.
 *
 * Multi-page: each HTML page is a build entry in `build.rollupOptions.input`
 * below. Add new pages there as the F3–F6 screens are finalized (dev `bun run dev`
 * serves any .html regardless; this list is what the production build emits).
 */
import { defineConfig } from "vite";

export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      // REST → Bun gateway (HTTP :3000), which proxies on to FastAPI :8000.
      "/api": { target: "http://localhost:3000", changeOrigin: true },
      // WebSocket → Bun gateway (:3001) for live map/notification events.
      "/ws": { target: "ws://localhost:3001", ws: true, changeOrigin: true },
    },
  },
  build: {
    rollupOptions: {
      // One entry per page (paths relative to this folder = the Vite root).
      input: {
        main: "index.html",
        about: "src/pages/about.html",
        login: "src/pages/login.html",
        register: "src/pages/register.html",
        forgotPassword: "src/pages/forgot-password.html",
        dashboard: "src/pages/dashboard.html",
        createService: "src/pages/create-service.html",
        serviceDetail: "src/pages/service-detail.html",
        myServices: "src/pages/my-services.html",
        mapView: "src/pages/map-view.html",
        notifications: "src/pages/notifications.html",
        profile: "src/pages/profile.html",
        provider: "src/pages/provider.html",
      },
    },
  },
});
