import { apiGet } from "./api.js";
import { describeWeekdays, formatDateRange, formatShortDate } from "./dates.js";
import { drawNav } from "./nav.js";
import type { Leave, MyLeavesResponse } from "./types.js";

function describeUnderDates(leave: Leave): string {
  if (leave.status === "rejected" && leave.decision_comment) {
    return `${leave.approver_name}: ${leave.decision_comment}`;
  }
  return describeWeekdays(leave.start_date, leave.end_date);
}

function setText(id: string, text: string | number): void {
  document.getElementById(id)!.textContent = String(text);
}

export function fillLeavesTable(leaves: Leave[]): void {
  document.getElementById("no-requests")!.hidden = leaves.length > 0;
  document.getElementById("requests-table")!.hidden = leaves.length === 0;
  const template = document.getElementById("leave-row") as HTMLTemplateElement;
  const rows = leaves.map((leave) => {
    const row = template.content.cloneNode(true) as DocumentFragment;
    row.querySelector("tr")!.dataset.leaveId = String(leave.id);
    row.querySelector(".dates")!.textContent = formatDateRange(leave.start_date, leave.end_date);
    row.querySelector(".note")!.textContent = describeUnderDates(leave);
    row.querySelector(".days")!.textContent = String(leave.days);
    const badge = row.querySelector(".badge")!;
    badge.classList.add(`badge-${leave.status}`);
    badge.textContent = leave.status;
    row.querySelector(".approver")!.textContent = leave.approver_name;
    row.querySelector(".submitted")!.textContent = formatShortDate(leave.submitted_at);
    return row;
  });
  document.getElementById("requests-body")!.replaceChildren(...rows);
  setText("table-footer", `Showing ${leaves.length} of ${leaves.length} requests`);
}

export function fillSummary(summary: MyLeavesResponse["summary"], year: number, onProbation = false): void {
  setText("summary-year", year);
  setText("days-taken", summary.days_taken);
  setText("limit-note", onProbation ? "2 days a month while on probation" : "no yearly limit");
  setText("pending-count", summary.pending_count);
  setText("pending-unit", summary.pending_count === 1 ? "request" : "requests");
  setText("waiting-note", summary.pending_count > 0 ? "awaiting a decision" : "nothing waiting");
}

export async function initMyLeaves(): Promise<void> {
  const me = await drawNav("/");
  const response = await apiGet<MyLeavesResponse>("/api/leaves");
  document.getElementById("apply-button")!.hidden = me.approver === null;
  fillSummary(response.summary, new Date().getFullYear(), me.on_probation);
  fillLeavesTable(response.leaves);
}

if (typeof document !== "undefined" && document.body?.dataset.page === "myLeaves") void initMyLeaves();
