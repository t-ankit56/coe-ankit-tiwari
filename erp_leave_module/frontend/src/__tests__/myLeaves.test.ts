import { beforeEach, describe, expect, it } from "vitest";
import { fillLeavesTable } from "../myLeaves.js";
import type { Leave } from "../types.js";
import { loadPage } from "./loadPage.js";

function makeLeave(overrides: Partial<Leave> = {}): Leave {
  return {
    id: 1,
    start_date: "2026-11-23",
    end_date: "2026-11-27",
    half_day: false,
    days: 4,
    reason: "Family trip",
    status: "pending",
    approver_name: "Priya Nair",
    decision_comment: "",
    submitted_at: "2026-11-06T10:00:00+05:30",
    ...overrides,
  };
}

beforeEach(() => {
  loadPage("my_leaves");
});

describe("leaves table", () => {
  it('shows "No requests yet" and no table when there are none', () => {
    fillLeavesTable([]);

    expect(document.getElementById("no-requests")!.hidden).toBe(false);
    expect(document.getElementById("no-requests")!.textContent).toContain("No requests yet");
    expect(document.getElementById("requests-table")!.hidden).toBe(true);
  });

  it("shows one row per request with its status badge", () => {
    fillLeavesTable([
      makeLeave({ id: 1, status: "pending" }),
      makeLeave({ id: 2, status: "approved", start_date: "2026-07-08", end_date: "2026-07-10" }),
    ]);
    const table = document.getElementById("requests-table")!;

    expect(table.hidden).toBe(false);
    expect(document.getElementById("no-requests")!.hidden).toBe(true);
    expect(document.querySelectorAll("#requests-body tr")).toHaveLength(2);
    expect(table.querySelector(".badge-pending")).not.toBeNull();
    expect(table.querySelector(".badge-approved")).not.toBeNull();
    expect(table.textContent).toContain("23 – 27 Nov 2026");
    expect(table.textContent).toContain("Mon to Fri");
    expect(table.textContent).toContain("8 – 10 Jul 2026");
    expect(table.textContent).toContain("6 Nov");
    expect(table.textContent).toContain("Priya Nair");
  });
});

describe("rejected request", () => {
  it("shows the rejection comment under the dates as plain text", () => {
    fillLeavesTable([
      makeLeave({ status: "rejected", decision_comment: "<b>x</b> Release day", approver_name: "Priya Nair" }),
    ]);
    const row = document.querySelector("#requests-body tr")!;

    expect(row.querySelector(".note")!.textContent).toBe("Priya Nair: <b>x</b> Release day");
    expect(row.querySelector("b")).toBeNull();
  });
});
