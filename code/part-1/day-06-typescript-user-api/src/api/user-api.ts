import { isUser } from "../guards/is-user.js";
import type { User } from "../models/user.js";

/** The part of fetch that fetchUser needs: a URL in, a Response-like out. */
export type FetchFn = (url: string) => Promise<{
  ok: boolean;
  status: number;
  json(): Promise<unknown>;
}>;

const BASE_URL = "https://jsonplaceholder.typicode.com";

/** Fetches one user and returns it only if the JSON passes isUser. */
export async function fetchUser(id: number, fetchFn: FetchFn): Promise<User> {
  const response = await fetchFn(`${BASE_URL}/users/${id}`);
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  const body: unknown = await response.json();
  if (!isUser(body)) {
    throw new Error("Response is not a valid user");
  }
  return body;
}
