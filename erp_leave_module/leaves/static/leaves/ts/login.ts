import type { CurrentUser } from "./types.js";

export async function submitLogin(email: string, password: string): Promise<CurrentUser> {
  throw new Error("NotImplementedError");
}

export function initLogin(): void {
  throw new Error("NotImplementedError");
}

if (typeof document !== "undefined" && document.body?.dataset.page === "login") initLogin();
