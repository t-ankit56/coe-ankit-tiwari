import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { mountApprovalsPage, renderWaitingList } from "../approvals.js";
import type { WaitingApproval } from "../types.js";

function makeWaitingApproval(overrides: Partial<WaitingApproval> = {}): WaitingApproval {
  return {
    id: 7,
    start_date: "2026-12-24",
    end_date: "2026-12-28",
    half_day: false,
    days: 2,
    reason: "Holiday",
    status: "pending",
    approver_name: "Priya Nair",
    decision_comment: "",
    submitted_at: "2026-11-02T10:00:00+05:30",
    requester_name: "Ankit Tiwari",
    requester_email: "ankit@incubyte.co",
    ...overrides,
  };
}

beforeEach(() => {
  document.body.innerHTML = '<main id="main"></main>';
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("waiting list", () => {
  it('shows "No requests waiting" when empty', () => {
    expect(renderWaitingList([], null)).toContain("No requests waiting");
  });
});

describe("reject button", () => {
  it("stays disabled until the comment has real text", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => [makeWaitingApproval()] }),
    );
    await mountApprovalsPage(document.getElementById("main")!);
    const comment = document.querySelector<HTMLTextAreaElement>("#decision-comment")!;
    const reject = document.querySelector<HTMLButtonElement>("#reject")!;

    expect(reject.disabled).toBe(true);

    comment.value = "   ";
    comment.dispatchEvent(new Event("input", { bubbles: true }));
    expect(reject.disabled).toBe(true);

    comment.value = "Release day";
    comment.dispatchEvent(new Event("input", { bubbles: true }));
    expect(reject.disabled).toBe(false);
  });
});
