import { isUser } from "../guards/is-user.js";
import type { User } from "../models/user.js";

/** The part of fetch that fetchUser needs: a URL in, a Response-like out. */
export type FetchFn = (url: string) => Promise<{
  ok: boolean;
  status: number;
  json(): Promise<unknown>;
}>;

const BASE_URL = "https://jsonplaceholder.typicode.com";

/** Fetches one user. Rejects on a network error, a bad status or JSON that fails isUser. */
export async function fetchUser(id: number, fetchFn: FetchFn): Promise<User> {
  let response;
  try {
    response = await fetchFn(`${BASE_URL}/users/${id}`);
  } catch (error) {
    throw new Error(`Could not reach the API for user ${id}`, { cause: error });
  }
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  const body: unknown = await response.json();
  if (!isUser(body)) {
    throw new Error("Response is not a valid user");
  }
  return body;
}
