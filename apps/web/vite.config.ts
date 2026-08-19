import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const reviewHosts = process.env.VITE_REVIEW_HOST ? [process.env.VITE_REVIEW_HOST] : [];

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5188,
    allowedHosts: reviewHosts,
    proxy: {
      "/api": { target: "http://127.0.0.1:4800", changeOrigin: true, rewrite: (path) => path.replace(/^\/api/, "") },
      "/media": { target: "http://127.0.0.1:4800", changeOrigin: true },
    },
  },
});
