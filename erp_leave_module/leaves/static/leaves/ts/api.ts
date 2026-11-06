import type { ApiErrorBody } from "./types.js";

export const navigation = {
  goTo(url: string): void {
    window.location.assign(url);
  },
};

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function readJsonOrThrow<T>(response: Response): Promise<T> {
  if (response.status === 401) {
    navigation.goTo("/login");
    throw new ApiError(401, "Please log in.");
  }
  if (response.status === 204) {
    return undefined as T;
  }
  const body = await response.json();
  if (!response.ok) {
    throw new ApiError(response.status, (body as ApiErrorBody).error);
  }
  return body as T;
}

export async function apiGet<T>(path: string): Promise<T> {
  return readJsonOrThrow<T>(await fetch(path));
}

function readCookie(name: string): string {
  const match = document.cookie.split("; ").find((cookie) => cookie.startsWith(`${name}=`));
  return match ? decodeURIComponent(match.slice(name.length + 1)) : "";
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": readCookie("csrftoken") },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  return readJsonOrThrow<T>(response);
}
