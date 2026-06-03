import { defineConfig } from "vite";

/** Для GitHub Pages: /имя-репозитория/ — задаётся в CI через VITE_BASE_PATH */
const base = process.env.VITE_BASE_PATH ?? "/";

export default defineConfig({
  base,
});
