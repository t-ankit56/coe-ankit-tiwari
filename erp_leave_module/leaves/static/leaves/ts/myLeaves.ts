import type { Leave, MyLeavesResponse } from "./types.js";

export function renderLeavesTable(leaves: Leave[]): string {
  return "<p>No requests yet</p>";
}

export function renderSummaryCards(summary: MyLeavesResponse["summary"], year: number): string {
  throw new Error("NotImplementedError");
}

export async function initMyLeaves(): Promise<void> {
  throw new Error("NotImplementedError");
}
