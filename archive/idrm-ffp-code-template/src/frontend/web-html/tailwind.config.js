/**
 * tailwind.config.js — IDRM web-html theme (Slate + Emerald + Inter).
 *
 * The palette IS Tailwind's built-in `slate` / `emerald` / `amber` / `red` — use
 * those classes directly (see instructions/instructions_ui_v3.md, the canonical
 * rulebook). The only things configured here are the Inter font and an optional
 * `primary` alias (so `bg-primary` works and a future dark mode is easier).
 */
/** @type {import('tailwindcss').Config} */
export default {
  // Files Tailwind scans for class names (so it only ships the CSS you actually use).
  content: ["./index.html", "./src/**/*.{html,js,ts}"],
  theme: {
    extend: {
      fontFamily: { sans: ["Inter", "system-ui", "-apple-system", "sans-serif"] },
      colors: {
        primary: { DEFAULT: "#059669", hover: "#047857", light: "#d1fae5", dark: "#065f46" },
      },
    },
  },
  plugins: [],
};
