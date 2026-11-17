import type { User } from "../models/user.js";

/** Type guard: true only if the unknown value has the shape of a User. */
export function isUser(value: unknown): value is User {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  return "email" in value && typeof value.email === "string";
}
