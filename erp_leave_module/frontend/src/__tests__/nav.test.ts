import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { drawNav } from "../nav.js";
import type { CurrentUser } from "../types.js";
import { loadPage } from "./loadPage.js";

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

async function drawNavFor(user: CurrentUser): Promise<void> {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => user }));
  await drawNav("/");
}

function linkIsShown(id: string): boolean {
  const link = document.getElementById(id);
  return link !== null && !link.hidden;
}

beforeEach(() => {
  loadPage("my_leaves");
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("nav", () => {
  it("hides the Apply link when the user has no approver", async () => {
    await drawNavFor(makeUser({ approver: null }));

    expect(linkIsShown("nav-my-leaves")).toBe(true);
    expect(linkIsShown("nav-apply")).toBe(false);
  });

  it("shows the Apply link when the user has an approver", async () => {
    await drawNavFor(makeUser());

    expect(linkIsShown("nav-apply")).toBe(true);
  });

  it("shows the Approvals link only for approvers", async () => {
    await drawNavFor(makeUser({ is_approver: true }));
    expect(linkIsShown("nav-approvals")).toBe(true);

    loadPage("my_leaves");
    await drawNavFor(makeUser({ is_approver: false }));
    expect(linkIsShown("nav-approvals")).toBe(false);
  });
});
