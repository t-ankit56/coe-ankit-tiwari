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

  it("shows one row per request with its status badge", () => {
    const html = renderLeavesTable([
      makeLeave({ id: 1, status: "pending" }),
      makeLeave({ id: 2, status: "approved", start_date: "2026-07-08", end_date: "2026-07-10" }),
    ]);

    expect(html.match(/<tr data-leave-id/g)).toHaveLength(2);
    expect(html).toContain('class="badge badge-pending"');
    expect(html).toContain('class="badge badge-approved"');
    expect(html).toContain("23 – 27 Nov 2026");
    expect(html).toContain("Mon to Fri");
    expect(html).toContain("8 – 10 Jul 2026");
    expect(html).toContain("6 Nov");
    expect(html).toContain("Priya Nair");
    expect(html).not.toContain("No requests yet");
  });
});
