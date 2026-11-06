import { apiGet } from "./api.js";
import { describeWeekdays, formatDateRange, formatShortDate } from "./dates.js";
import { escapeHtml } from "./html.js";
import { drawNav } from "./nav.js";
import type { Leave, MyLeavesResponse } from "./types.js";

function renderLeaveRow(leave: Leave): string {
  return `<tr data-leave-id="${leave.id}">
    <td><strong>${formatDateRange(leave.start_date, leave.end_date)}</strong><span class="note">${describeWeekdays(leave.start_date, leave.end_date)}</span></td>
    <td>${leave.days}</td>
    <td><span class="badge badge-${leave.status}">${leave.status}</span></td>
    <td>${escapeHtml(leave.approver_name)}</td>
    <td class="muted">${formatShortDate(leave.submitted_at)}</td>
  </tr>`;
}

export function renderLeavesTable(leaves: Leave[]): string {
  if (leaves.length === 0) {
    return "<p>No requests yet</p>";
  }
  const rows = leaves.map(renderLeaveRow).join("");
  return `<table><thead><tr><th>Dates</th><th>Days</th><th>Status</th><th>Approver</th><th>Submitted</th></tr></thead><tbody>${rows}</tbody></table>`;
}

export function renderSummaryCards(summary: MyLeavesResponse["summary"], year: number): string {
  return `<div class="cards">
    <div class="card"><span class="card-number">${summary.days_taken}</span> Personal days taken in ${year}</div>
    <div class="card"><span class="card-number">${summary.pending_count}</span> Requests waiting for approval</div>
  </div>`;
}

export async function initMyLeaves(): Promise<void> {
  await drawNav("/");
  const response = await apiGet<MyLeavesResponse>("/api/leaves");
  const main = document.getElementById("main")!;
  main.innerHTML = `<h1>My leaves</h1>${renderSummaryCards(response.summary, new Date().getFullYear())}${renderLeavesTable(response.leaves)}`;
}

if (typeof document !== "undefined" && document.body?.dataset.page === "myLeaves") void initMyLeaves();
