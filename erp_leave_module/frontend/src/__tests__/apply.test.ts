import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { mountApplyPage } from "../apply.js";
import type { CurrentUser, LeavePreview } from "../types.js";
import { loadPage } from "./loadPage.js";

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

function isShown(id: string): boolean {
  const element = document.getElementById(id);
  return element !== null && !element.hidden;
}

beforeEach(() => {
  loadPage("apply");
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("apply page", () => {
  it("shows the day count after valid dates are entered", async () => {
    const fetchSpy = answerPreviewWith(thanksgivingWeek);
    mountApplyPage(ankit);

    typeInto("#start-date", "2026-11-23");
    typeInto("#end-date", "2026-11-27");

    await vi.waitFor(() => expect(isShown("preview-result")).toBe(true));
    expect(isShown("preview-empty")).toBe(false);
    expect(document.getElementById("preview-days")!.textContent).toBe("4 working days");
    expect(document.getElementById("preview-panel")!.textContent).toContain("Thanksgiving, not counted");
    expect(fetchSpy.mock.calls[0][0]).toBe("/api/leaves/preview?start_date=2026-11-23&end_date=2026-11-27&half=false");
  });
});

const aarav: CurrentUser = { ...ankit, id: 2, name: "Aarav Singh", email: "aarav@incubyte.co", on_probation: true };

const overTheProbationLimit: LeavePreview = {
  days: 2,
  breakdown: [
    { date: "2026-11-19", counts: 1, label: null },
    { date: "2026-11-20", counts: 1, label: null },
  ],
  overlap: null,
  probation: {
    ok: false,
    limit: 2,
    months: [{ month: "2026-11", used: 1.5, requested: 2, left: 0.5, over: 1.5 }],
    suggestion: { start_date: "2026-11-19", end_date: "2026-11-19", half_day: true },
  },
};

describe("over the probation limit", () => {
  it("shows the warning and disables Submit", async () => {
    answerPreviewWith(overTheProbationLimit);
    mountApplyPage(aarav);

    typeInto("#reason", "Cousin's wedding");
    typeInto("#start-date", "2026-11-19");
    typeInto("#end-date", "2026-11-20");

    await vi.waitFor(() => expect(isShown("probation-warning")).toBe(true));
    expect(isShown("preview-result")).toBe(false);
    const panelText = document.getElementById("preview-panel")!.textContent!;
    expect(panelText).toContain("1.5 of 2 days used");
    expect(panelText).toContain("1.5 days over the limit");
    expect(document.querySelector<HTMLButtonElement>("#submit")!.disabled).toBe(true);
    expect(document.getElementById("apply-form")!.textContent).toContain("Change the dates to continue.");
  });
});

describe("suggestion button", () => {
  it("fills in the dates and half-day box and refreshes the preview", async () => {
    const halfDayThursday: LeavePreview = {
      days: 0.5,
      breakdown: [{ date: "2026-11-19", counts: 0.5, label: null }],
      overlap: null,
      probation: {
        ok: true,
        limit: 2,
        months: [{ month: "2026-11", used: 1.5, requested: 0.5, left: 0.5, over: 0 }],
        suggestion: null,
      },
    };
    const fetchSpy = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => overTheProbationLimit })
      .mockResolvedValue({ ok: true, status: 200, json: async () => halfDayThursday });
    vi.stubGlobal("fetch", fetchSpy);
    mountApplyPage(aarav);
    typeInto("#start-date", "2026-11-19");
    typeInto("#end-date", "2026-11-20");
    await vi.waitFor(() => expect(isShown("use-suggestion")).toBe(true));

    document.getElementById("use-suggestion")!.click();

    await vi.waitFor(() => expect(isShown("preview-result")).toBe(true));
    expect(isShown("probation-warning")).toBe(false);
    expect(document.getElementById("preview-panel")!.textContent).toContain("Within your probation limit");
    expect(document.querySelector<HTMLInputElement>("#start-date")!.value).toBe("2026-11-19");
    expect(document.querySelector<HTMLInputElement>("#end-date")!.value).toBe("2026-11-19");
    expect(document.querySelector<HTMLInputElement>("#half-day")!.checked).toBe(true);
    expect(fetchSpy.mock.calls.at(-1)![0]).toBe(
      "/api/leaves/preview?start_date=2026-11-19&end_date=2026-11-19&half=true",
    );
  });
});
