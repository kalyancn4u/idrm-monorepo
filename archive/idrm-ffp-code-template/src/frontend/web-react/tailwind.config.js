/**
 * tailwind.config.js — IDRM admin SPA (same Slate + Emerald + Inter tokens as the
 * HTML frontend; see instructions/instructions_ui_v3.md).
 */
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
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
