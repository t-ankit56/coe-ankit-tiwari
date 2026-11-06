import type { CurrentUser } from "./types.js";

export function renderNav(me: CurrentUser, currentPath: string): string {
  return `<nav><a href="/">My leaves</a></nav>`;
}
