// @ts-check
import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import sitemap from "@astrojs/sitemap";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  site: "https://coredispatch.xyz",
  integrations: [react(), sitemap({ filter: (page) => !page.includes("/staging") })],
  vite: {
    plugins: [tailwindcss()],
    server: {
      host: "0.0.0.0",
      port: 3000,
      watch: {
        usePolling: true,
        interval: 1000,
      },
      proxy: {
        "/api": "http://localhost:8000",
      },
    },
  },
});
