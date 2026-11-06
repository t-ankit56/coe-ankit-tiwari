import { describe, expect, it } from "vitest";
import { renderNav } from "../nav.js";
import type { CurrentUser } from "../types.js";

function makeUser(overrides: Partial<CurrentUser> = {}): CurrentUser {
  return {
    id: 1,
    name: "Ankit Tiwari",
    email: "ankit@incubyte.co",
    is_approver: false,
    on_probation: false,
    approver: { name: "Priya Nair" },
    ...overrides,
  };
}

describe("nav", () => {
  it("hides the Apply button when the user has no approver", () => {
    const html = renderNav(makeUser({ approver: null }), "/");

    expect(html).toContain("My leaves");
    expect(html).not.toContain("Apply");
  });
});
