import { apiGet } from "./api.js";
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

export async function drawNav(currentPath: string): Promise<CurrentUser> {
  const me = await apiGet<CurrentUser>("/api/me");
  const navElement = document.getElementById("nav");
  if (navElement) {
    navElement.innerHTML = renderNav(me, currentPath);
  }
  return me;
}
