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
    return '<p class="empty">No requests yet</p>';
  }
  const rows = leaves.map(renderLeaveRow).join("");
  return `<table class="requests"><thead><tr><th>Dates</th><th>Days</th><th>Status</th><th>Approver</th><th>Submitted</th></tr></thead><tbody>${rows}</tbody></table>`;
}

export function renderSummaryCards(
  summary: MyLeavesResponse["summary"],
  year: number,
  onProbation = false,
): string {
  const limitNote = onProbation ? "2 days a month while on probation" : "no yearly limit";
  const waitingNote = summary.pending_count > 0 ? "awaiting a decision" : "nothing waiting";
  return `<section class="summary" aria-label="Summary">
    <div class="summary-cell"><span class="muted">Personal leave in ${year}</span>
      <span class="summary-number">${summary.days_taken} <span class="summary-unit">days taken</span></span>
      <span class="muted">${limitNote}</span></div>
    <div class="summary-cell"><span class="muted">Waiting for approval</span>
      <span class="summary-number">${summary.pending_count} <span class="summary-unit">${summary.pending_count === 1 ? "request" : "requests"}</span></span>
      <span class="muted">${waitingNote}</span></div>
  </section>`;
}

export async function initMyLeaves(): Promise<void> {
  const me = await drawNav("/");
  const response = await apiGet<MyLeavesResponse>("/api/leaves");
  const applyButton = me.approver !== null ? '<a class="btn btn-primary" href="/apply">+ Apply for leave</a>' : "";
  document.getElementById("main")!.innerHTML = `<div class="page">
    <header class="page-header">
      <div><span class="breadcrumb">Leave / My leaves</span><h1>My leaves</h1></div>
      ${applyButton}
    </header>
    ${renderSummaryCards(response.summary, new Date().getFullYear(), me.on_probation)}
    <section class="card table-card" aria-labelledby="requests-title">
      <h2 id="requests-title" class="card-title">All my requests</h2>
      ${renderLeavesTable(response.leaves)}
      <p class="table-footer muted">Showing ${response.leaves.length} of ${response.leaves.length} requests</p>
    </section>
  </div>`;
}

if (typeof document !== "undefined" && document.body?.dataset.page === "myLeaves") void initMyLeaves();
