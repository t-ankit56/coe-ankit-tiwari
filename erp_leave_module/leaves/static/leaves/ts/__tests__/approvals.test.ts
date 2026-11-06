import { describe, expect, it } from "vitest";
import { renderWaitingList } from "../approvals.js";

describe("waiting list", () => {
  it('shows "No requests waiting" when empty', () => {
    expect(renderWaitingList([], null)).toContain("No requests waiting");
  });
});
