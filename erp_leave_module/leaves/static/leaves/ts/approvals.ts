import { apiGet } from "./api.js";
import { formatDateRange, formatShortDate } from "./dates.js";
import { escapeHtml } from "./html.js";
import { drawNav } from "./nav.js";
import type { WaitingApproval } from "./types.js";

function initialsOf(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
}

export function renderWaitingList(items: WaitingApproval[], selectedId: number | null): string {
  if (items.length === 0) {
    return '<p class="empty">No requests waiting</p>';
  }
  const rows = items
    .map(
      (item) => `<button type="button" class="waiting-item${item.id === selectedId ? " selected" : ""}" data-leave-id="${item.id}">
        <span class="avatar avatar-light" aria-hidden="true">${escapeHtml(initialsOf(item.requester_name))}</span>
        <span class="waiting-text"><strong>${escapeHtml(item.requester_name)}</strong>
          <span class="muted">Personal · ${formatDateRange(item.start_date, item.end_date)}</span></span>
        <span class="waiting-days"><strong>${item.days}</strong><span class="muted small">${item.days === 1 ? "day" : "days"}</span></span>
      </button>`,
    )
    .join("");
  return `<div class="waiting-items">${rows}</div>`;
}

export function renderDecisionPanel(item: WaitingApproval): string {
  return `<div class="requester"><span class="avatar avatar-light" aria-hidden="true">${escapeHtml(initialsOf(item.requester_name))}</span>
      <div><h2 class="card-title">${escapeHtml(item.requester_name)}</h2><span class="muted">${escapeHtml(item.requester_email)}</span></div></div>
    <dl class="details">
      <dt>Dates</dt><dd><strong>${formatDateRange(item.start_date, item.end_date)}</strong></dd>
      <dt>Days</dt><dd><strong>${item.days} working ${item.days === 1 ? "day" : "days"}</strong></dd>
      <dt>Reason</dt><dd>${escapeHtml(item.reason)}</dd>
      <dt>Submitted</dt><dd>${formatShortDate(item.submitted_at)}</dd>
    </dl>
    <div class="field"><label class="label" for="decision-comment">Comment <span class="muted">(required if you reject)</span></label>
      <textarea id="decision-comment" rows="3"></textarea></div>
    <div class="actions">
      <button id="approve" class="btn btn-primary" type="button">Approve</button>
      <button id="reject" class="btn btn-reject" type="button" disabled>Reject</button>
      <span id="decision-message" class="small error"></span>
    </div>`;
}

export async function mountApprovalsPage(main: HTMLElement): Promise<void> {
  const items = await apiGet<WaitingApproval[]>("/api/approvals");
  let selectedId: number | null = items.length > 0 ? items[0].id : null;

  main.innerHTML = `<div class="page">
    <header class="page-header"><div><span class="breadcrumb">Leave / Approvals</span><h1>Approvals</h1></div></header>
    <div class="approvals-layout">
      <section class="card list-card"><div class="list-header"><h2 class="card-title">Requests from your team</h2><span class="muted small">Sorted by start date</span></div>
        <div id="waiting-list"></div></section>
      <section id="decision-panel" class="card side-card"></section>
    </div>
  </div>`;
  const list = main.querySelector<HTMLElement>("#waiting-list")!;
  const panel = main.querySelector<HTMLElement>("#decision-panel")!;

  function render(): void {
    list.innerHTML = renderWaitingList(items, selectedId);
    const selected = items.find((item) => item.id === selectedId);
    panel.innerHTML = selected ? renderDecisionPanel(selected) : '<p class="empty">Nothing to decide right now.</p>';
    const comment = panel.querySelector<HTMLTextAreaElement>("#decision-comment");
    const reject = panel.querySelector<HTMLButtonElement>("#reject");
    comment?.addEventListener("input", () => {
      reject!.disabled = comment.value.trim() === "";
    });
  }

  list.addEventListener("click", (event) => {
    const row = (event.target as HTMLElement).closest<HTMLElement>("[data-leave-id]");
    if (row) {
      selectedId = Number(row.dataset.leaveId);
      render();
    }
  });
  render();
}

export async function initApprovals(): Promise<void> {
  await drawNav("/approvals");
  await mountApprovalsPage(document.getElementById("main")!);
}

if (typeof document !== "undefined" && document.body?.dataset.page === "approvals") void initApprovals();
