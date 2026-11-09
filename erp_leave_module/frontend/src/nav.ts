import { apiGet, apiPost, navigation } from "./api.js";
import { escapeHtml } from "./html.js";
import type { CurrentUser } from "./types.js";

function initialsOf(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
}

export function renderNav(me: CurrentUser, currentPath: string): string {
  const links = [{ href: "/", label: "My leaves" }];
  if (me.approver !== null) {
    links.push({ href: "/apply", label: "Apply" });
  }
  if (me.is_approver) {
    links.push({ href: "/approvals", label: "Approvals" });
  }
  const items = links
    .map((link) => `<a href="${link.href}"${link.href === currentPath ? ' aria-current="page"' : ""}>${link.label}</a>`)
    .join("");
  return `<aside class="sidebar">
    <div class="brand"><img src="/incubyte-logo.png" alt="Incubyte"></div>
    <nav aria-label="Main">
      <p class="nav-group">Leave</p>
      <div class="nav-links">${items}</div>
    </nav>
    <div class="user">
      <span class="avatar" aria-hidden="true">${escapeHtml(initialsOf(me.name))}</span>
      <span class="user-text"><strong>${escapeHtml(me.name)}</strong><span class="muted">${escapeHtml(me.email)}</span></span>
      <button type="button" id="logout" class="link-button">Log out</button>
    </div>
  </aside>`;
}

export async function drawNav(currentPath: string): Promise<CurrentUser> {
  const me = await apiGet<CurrentUser>("/api/me");
  const navElement = document.getElementById("nav");
  if (navElement) {
    navElement.innerHTML = renderNav(me, currentPath);
    document.getElementById("logout")?.addEventListener("click", async () => {
      await apiPost("/api/logout");
      navigation.goTo("/login");
    });
  }
  return me;
}
