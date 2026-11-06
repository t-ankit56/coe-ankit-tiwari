import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { mountApplyPage } from "../apply.js";
import type { CurrentUser, LeavePreview } from "../types.js";

const ankit: CurrentUser = {
  id: 1,
  name: "Ankit Tiwari",
  email: "ankit@incubyte.co",
  is_approver: false,
  on_probation: false,
  approver: { name: "Priya Nair" },
};

const thanksgivingWeek: LeavePreview = {
  days: 4,
  breakdown: [
    { date: "2026-11-23", counts: 1, label: null },
    { date: "2026-11-24", counts: 1, label: null },
    { date: "2026-11-25", counts: 1, label: null },
    { date: "2026-11-26", counts: 1, label: null },
    { date: "2026-11-27", counts: 0, label: "Thanksgiving, not counted" },
  ],
  overlap: null,
  probation: null,
};

function answerPreviewWith(preview: LeavePreview) {
  const fetchSpy = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => preview });
  vi.stubGlobal("fetch", fetchSpy);
  return fetchSpy;
}

function typeInto(selector: string, value: string) {
  const input = document.querySelector<HTMLInputElement>(selector)!;
  input.value = value;
  input.dispatchEvent(new Event("input", { bubbles: true }));
}

beforeEach(() => {
  document.body.innerHTML = '<main id="main"></main>';
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("apply page", () => {
  it("shows the day count after valid dates are entered", async () => {
    const fetchSpy = answerPreviewWith(thanksgivingWeek);
    mountApplyPage(document.getElementById("main")!, ankit);

    typeInto("#start-date", "2026-11-23");
    typeInto("#end-date", "2026-11-27");

    await vi.waitFor(() => {
      expect(document.getElementById("preview-panel")!.textContent).toContain("4 working days");
    });
    expect(document.getElementById("preview-panel")!.textContent).toContain("Thanksgiving, not counted");
    expect(fetchSpy.mock.calls[0][0]).toBe("/api/leaves/preview?start_date=2026-11-23&end_date=2026-11-27&half=false");
  });
});
