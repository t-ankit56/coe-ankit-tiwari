import { apiGet, apiPost, navigation } from "./api.js";
import type { CurrentUser } from "./types.js";

export function initialsOf(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
}

// The sidebar markup is in partials/sidebar.html. This only fills in the user and
// shows the links this user is allowed to use.
export async function drawNav(currentPath: string): Promise<CurrentUser> {
  const me = await apiGet<CurrentUser>("/api/me");
  document.getElementById("nav-apply")!.hidden = me.approver === null;
  document.getElementById("nav-approvals")!.hidden = !me.is_approver;
  document.querySelector(`.nav-links a[href="${currentPath}"]`)?.setAttribute("aria-current", "page");
  document.getElementById("user-initials")!.textContent = initialsOf(me.name);
  document.getElementById("user-name")!.textContent = me.name;
  document.getElementById("user-email")!.textContent = me.email;
  document.getElementById("logout")!.addEventListener("click", async () => {
    await apiPost("/api/logout");
    navigation.goTo("/login");
  });
  return me;
}
