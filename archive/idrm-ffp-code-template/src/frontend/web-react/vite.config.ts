/**
 * vite.config.ts — dev server + build for the IDRM admin SPA.
 * Serves on :5174 and proxies /api + /ws to the Bun gateway (:3000 / :3001), so
 * the app uses relative URLs (/api/v1/...) — same shape NGINX serves in prod.
 */
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      "/api": { target: "http://localhost:3000", changeOrigin: true },
      "/ws": { target: "ws://localhost:3001", ws: true, changeOrigin: true },
    },
  },
});
