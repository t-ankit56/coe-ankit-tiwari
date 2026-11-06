import { describe, expect, it } from "vitest";
import { renderLeavesTable } from "../myLeaves.js";
import type { Leave } from "../types.js";

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

describe("leaves table", () => {
  it('shows "No requests yet" when there are none', () => {
    expect(renderLeavesTable([])).toContain("No requests yet");
  });
});
