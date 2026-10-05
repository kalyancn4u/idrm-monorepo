/**
 * postcss.config.js — Vite runs this over the CSS. Tailwind generates the utility
 * classes (scanning the files in tailwind.config.js `content`); Autoprefixer adds
 * vendor prefixes for older browsers.
 */
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
