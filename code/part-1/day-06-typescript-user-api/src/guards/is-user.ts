import type { User } from "../models/user.js";

/** Type guard: true only if the unknown value has the shape of a User. */
export function isUser(value: unknown): value is User {
  return typeof value === "object" && value !== null;
}
