import { apiPost, navigation } from "./api.js";
import type { CurrentUser } from "./types.js";

export async function submitLogin(email: string, password: string): Promise<CurrentUser> {
  const user = await apiPost<CurrentUser>("/api/login", { email, password });
  navigation.goTo("/");
  return user;
}

export function initLogin(): void {
  // wired up once the login form is rendered (see the Task 1 demo step)
}

if (typeof document !== "undefined" && document.body?.dataset.page === "login") initLogin();
