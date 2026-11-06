import { apiPost, navigation } from "./api.js";
import type { CurrentUser } from "./types.js";

export async function submitLogin(email: string, password: string): Promise<CurrentUser> {
  const user = await apiPost<CurrentUser>("/api/login", { email, password });
  navigation.goTo("/");
  return user;
}

export function initLogin(): void {
  const main = document.getElementById("main")!;
  main.innerHTML = `<div class="login-card card">
      <img src="/static/leaves/img/incubyte-logo.png" alt="Incubyte" class="login-logo">
      <h1>Log in</h1>
      <form id="login-form">
        <div class="field"><label class="label" for="email">Email</label><input id="email" type="email" required></div>
        <div class="field"><label class="label" for="password">Password</label><input id="password" type="password" required></div>
        <button type="submit" class="btn btn-primary">Log in</button>
        <p id="message" class="small error"></p>
      </form>
    </div>`;
  main.querySelector("form")!.addEventListener("submit", async (event) => {
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
