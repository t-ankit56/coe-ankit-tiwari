import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { inlinePartials } from "../partials.js";

const frontendFolder = resolve(__dirname, "../..");

// Puts the real page (for example "apply" for apply.html) into the test document,
// with shared partials such as the sidebar already filled in.
export function loadPage(pageName: string): void {
  const html = readFileSync(resolve(frontendFolder, `${pageName}.html`), "utf8");
  const withPartials = inlinePartials(html, (path) => readFileSync(resolve(frontendFolder, path), "utf8"));
  const body = new DOMParser().parseFromString(withPartials, "text/html").body;
  document.body.innerHTML = body.innerHTML;
}
