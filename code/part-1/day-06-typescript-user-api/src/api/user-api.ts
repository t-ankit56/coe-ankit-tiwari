import type { User } from "../models/user.js";

export async function fetchUser(
  _id: number,
  _fetchFn: unknown,
): Promise<User> {
  throw new Error("not implemented");
}
