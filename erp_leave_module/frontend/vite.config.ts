import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { defineConfig } from "vite";
import { inlinePartials } from "./src/partials";

// The browser only talks to this dev server. It forwards /api to Django, so the session
// cookie and the CSRF header keep working on one origin. Leave changeOrigin off: Django
// compares the Origin and Host headers on POST, and both must stay localhost:5173.
const PAGE_FILES: Record<string, string> = {
  "/": "/my_leaves.html",
  "/login": "/login.html",
  "/apply": "/apply.html",
  "/approvals": "/approvals.html",
};

export default defineConfig({
  appType: "mpa",
  server: {
    port: 5173,
    proxy: { "/api": "http://localhost:8000" },
  },
  plugins: [
    {
      name: "html-partials",
      transformIndexHtml: {
        order: "pre",
        handler: (html: string) => inlinePartials(html, (path) => readFileSync(resolve(__dirname, path), "utf8")),
      },
    },
    {
      name: "page-routes",
      configureServer(server) {
        server.middlewares.use((request, _response, next) => {
          const path = (request.url ?? "").split("?")[0];
          if (PAGE_FILES[path]) request.url = PAGE_FILES[path];
          next();
        });
      },
    },
  ],
});
