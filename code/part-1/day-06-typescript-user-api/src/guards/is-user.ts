import type { User } from "../models/user.js";

function isObject(value: unknown): value is object {
  return typeof value === "object" && value !== null;
}

/** Type guard: true only if the unknown value has the shape of a User. */
export function isUser(value: unknown): value is User {
  if (!isObject(value)) {
    return false;
  }
  if (!("id" in value) || typeof value.id !== "number") {
    return false;
  }
  if (!("name" in value) || typeof value.name !== "string") {
    return false;
  }
  if (!("email" in value) || typeof value.email !== "string") {
    return false;
  }
  if (!("address" in value) || !isObject(value.address)) {
    return false;
  }
  return "city" in value.address && typeof value.address.city === "string";
}
