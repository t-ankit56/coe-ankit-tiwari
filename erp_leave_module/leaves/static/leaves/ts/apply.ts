import { apiGet } from "./api.js";
import { escapeHtml } from "./html.js";
import type { CurrentUser, LeavePreview } from "./types.js";

function describeDays(days: number): string {
  return `${days} working ${days === 1 ? "day" : "days"}`;
}

export function renderPreviewPanel(preview: LeavePreview): string {
  const rows = preview.breakdown
    .map(
      (day) =>
        `<li><span>${day.date}</span> <span>${day.counts}</span> <span>${escapeHtml(day.label ?? "")}</span></li>`,
    )
    .join("");
  return `<h2>What this request uses</h2><ul>${rows}</ul><p class="total">${describeDays(preview.days)}</p>`;
}

function renderApplyForm(me: CurrentUser): string {
  return `<form id="apply-form">
    <label>Start date <input id="start-date" type="date"></label>
    <label>End date <input id="end-date" type="date"></label>
    <label><input id="half-day" type="checkbox" disabled> Half day</label>
    <label>Reason <textarea id="reason"></textarea></label>
    <label>Approver <input id="approver" value="${escapeHtml(me.approver?.name ?? "")}" readonly></label>
    <button id="submit" type="submit">Submit</button>
  </form>
  <section id="preview-panel"></section>`;
}

export function mountApplyPage(main: HTMLElement, me: CurrentUser): void {
  main.innerHTML = renderApplyForm(me);
  const startDate = main.querySelector<HTMLInputElement>("#start-date")!;
  const endDate = main.querySelector<HTMLInputElement>("#end-date")!;
  const halfDay = main.querySelector<HTMLInputElement>("#half-day")!;
  const panel = main.querySelector<HTMLElement>("#preview-panel")!;

  async function refreshPreview(): Promise<void> {
    if (!startDate.value || !endDate.value) {
      panel.innerHTML = "";
      return;
    }
    const query = `start_date=${startDate.value}&end_date=${endDate.value}&half=${halfDay.checked}`;
    const preview = await apiGet<LeavePreview>(`/api/leaves/preview?${query}`);
    panel.innerHTML = renderPreviewPanel(preview);
  }

  for (const input of [startDate, endDate, halfDay]) {
    input.addEventListener("input", () => void refreshPreview());
  }
}

export async function initApply(): Promise<void> {
  throw new Error("NotImplementedError");
}
