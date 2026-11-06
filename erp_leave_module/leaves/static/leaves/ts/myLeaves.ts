import { escapeHtml } from "./html.js";
import type { Leave, MyLeavesResponse } from "./types.js";

const MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.slice(0, 10).split("-").map(Number);
  return `${day} ${MONTH_NAMES[month - 1]} ${year}`;
}

function renderLeaveRow(leave: Leave): string {
  const dates =
    leave.start_date === leave.end_date
      ? formatDate(leave.start_date)
      : `${formatDate(leave.start_date)} to ${formatDate(leave.end_date)}`;
  return `<tr data-leave-id="${leave.id}">
    <td>${dates}</td>
    <td>${leave.days}</td>
    <td><span class="badge badge-${leave.status}">${leave.status}</span></td>
    <td>${escapeHtml(leave.approver_name)}</td>
    <td>${formatDate(leave.submitted_at)}</td>
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
  throw new Error("NotImplementedError");
}

export async function initMyLeaves(): Promise<void> {
  throw new Error("NotImplementedError");
}
