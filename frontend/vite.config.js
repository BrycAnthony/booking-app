import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Default dev port is 5173 — the backend's ALLOWED_ORIGINS (see repo root .env)
// is set to http://localhost:5173, so changing this port will break CORS.
export default defineConfig({
  plugins: [react()],
});
