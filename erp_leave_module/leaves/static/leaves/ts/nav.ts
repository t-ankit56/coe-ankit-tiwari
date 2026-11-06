import type { CurrentUser } from "./types.js";

export function renderNav(me: CurrentUser, currentPath: string): string {
  const links = [{ href: "/", label: "My leaves" }];
  if (me.approver !== null) {
    links.push({ href: "/apply", label: "Apply" });
  }
  const items = links
    .map((link) => `<a href="${link.href}"${link.href === currentPath ? ' aria-current="page"' : ""}>${link.label}</a>`)
    .join("");
  return `<nav>${items}</nav>`;
}
