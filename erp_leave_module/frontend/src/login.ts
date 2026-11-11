import { apiPost, navigation } from "./api.js";
import type { CurrentUser } from "./types.js";

export async function submitLogin(email: string, password: string): Promise<CurrentUser> {
  const user = await apiPost<CurrentUser>("/api/login", { email, password });
  navigation.goTo("/");
  return user;
}

export function initLogin(): void {
  document.getElementById("login-form")!.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = (document.getElementById("email") as HTMLInputElement).value;
    const password = (document.getElementById("password") as HTMLInputElement).value;
    try {
      await submitLogin(email, password);
    } catch (error) {
      document.getElementById("message")!.textContent = error instanceof Error ? error.message : "Login failed.";
    }
  });
}

if (typeof document !== "undefined" && document.body?.dataset.page === "login") initLogin();
