import { apiGet, apiPost, navigation } from "./api.js";
import { escapeHtml } from "./html.js";
import { formatDayLabel } from "./dates.js";
import { drawNav } from "./nav.js";
import type { CurrentUser, LeavePreview } from "./types.js";

function describeDays(days: number): string {
  return `${days} working ${days === 1 ? "day" : "days"}`;
}

const CHECK_ICON =
  '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M8 12.5l2.5 2.5L16 9.5"></path></svg>';
const CROSS_ICON =
  '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M9 9l6 6M15 9l-6 6"></path></svg>';

export function renderEmptyPreviewPanel(): string {
  return '<h2 class="card-title">What this request uses</h2><p class="muted">Pick your dates to see how many working days this request uses.</p>';
}

export function renderPreviewPanel(preview: LeavePreview): string {
  const rows = preview.breakdown
    .map((day) => {
      const note = day.label ? `<span class="pill">${escapeHtml(day.label)}</span>` : "";
      const countClass = day.counts === 0 ? "day-count day-count-zero" : "day-count";
      return `<div class="day-row"><span>${formatDayLabel(day.date)} ${note}</span><span class="${countClass}">${day.counts}</span></div>`;
    })
    .join("");
  const first = preview.breakdown[0].date;
  const last = preview.breakdown[preview.breakdown.length - 1].date;
  const range = first === last ? formatDayLabel(first) : `${formatDayLabel(first)} – ${formatDayLabel(last)}`;
  const checks: string[] = [];
  if (preview.probation === null) {
    checks.push(`<li class="check-ok">${CHECK_ICON}<span>Personal leave has no yearly limit, so no balance is used.</span></li>`);
  }
  checks.push(
    preview.overlap
      ? `<li class="check-bad">${CROSS_ICON}<span>You already have leave on ${formatDayLabel(preview.overlap.start_date)} – ${formatDayLabel(preview.overlap.end_date)}.</span></li>`
      : `<li class="check-ok">${CHECK_ICON}<span>No overlap with your other requests.</span></li>`,
  );
  return `<h2 class="card-title">What this request uses</h2>
    <div><span class="big-number">${describeDays(preview.days)}</span><span class="muted block">${range} ${last.slice(0, 4)}</span></div>
    <div class="day-rows">${rows}</div>
    <ul class="checks">${checks.join("")}</ul>`;
}

function renderApplyForm(me: CurrentUser): string {
  const typeNote = me.on_probation ? "2 days a month while on probation" : "No yearly limit";
  return `<div class="page">
    <header class="page-header"><div><span class="breadcrumb">Leave / My leaves / Apply for leave</span><h1>Apply for leave</h1></div></header>
    <div class="apply-layout">
      <form id="apply-form" class="card form-card">
        <h2 class="card-title">Request details</h2>
        <div class="field"><span class="label">Leave type</span>
          <div class="type-card"><strong>Personal</strong><span class="muted">${typeNote}</span></div></div>
        <div class="field-row">
          <div class="field"><label class="label" for="start-date">From</label><input id="start-date" type="date"></div>
          <div class="field"><label class="label" for="end-date">To</label><input id="end-date" type="date"></div>
        </div>
        <div class="checkbox-row"><input id="half-day" type="checkbox" disabled><label for="half-day">Half day <span class="small">(only for a single day)</span></label></div>
        <div class="field"><label class="label" for="reason">Reason <span class="muted">(required)</span></label><textarea id="reason" rows="3"></textarea></div>
        <div class="field"><label class="label" for="approver">Approver</label>
          <input id="approver" class="readonly" value="${escapeHtml(me.approver?.name ?? "")}" readonly>
          <span class="small muted">Set by HR. If this is wrong, ask HR to change it.</span></div>
        <div class="actions">
          <button id="submit" class="btn btn-primary" type="submit">Submit request</button>
          <button id="cancel" class="btn btn-secondary" type="button">Cancel</button>
          <span id="message" class="small error"></span>
        </div>
      </form>
      <section id="preview-panel" class="card side-card">${renderEmptyPreviewPanel()}</section>
    </div>
  </div>`;
}

export function mountApplyPage(main: HTMLElement, me: CurrentUser): void {
  main.innerHTML = renderApplyForm(me);
  const form = main.querySelector<HTMLFormElement>("#apply-form")!;
  const startDate = main.querySelector<HTMLInputElement>("#start-date")!;
  const endDate = main.querySelector<HTMLInputElement>("#end-date")!;
  const halfDay = main.querySelector<HTMLInputElement>("#half-day")!;
  const reason = main.querySelector<HTMLTextAreaElement>("#reason")!;
  const submit = main.querySelector<HTMLButtonElement>("#submit")!;
  const panel = main.querySelector<HTMLElement>("#preview-panel")!;
  const message = main.querySelector<HTMLElement>("#message")!;
  let previewIsUsable = false;

  function updateSubmitState(): void {
    submit.disabled = !(startDate.value && endDate.value && reason.value.trim() && previewIsUsable);
  }

  async function refreshPreview(): Promise<void> {
    halfDay.disabled = !startDate.value || startDate.value !== endDate.value;
    if (halfDay.disabled) halfDay.checked = false;
    previewIsUsable = false;
    message.textContent = "";
    if (!startDate.value || !endDate.value) {
      panel.innerHTML = renderEmptyPreviewPanel();
      updateSubmitState();
      return;
    }
    const query = `start_date=${startDate.value}&end_date=${endDate.value}&half=${halfDay.checked}`;
    try {
      const preview = await apiGet<LeavePreview>(`/api/leaves/preview?${query}`);
      panel.innerHTML = renderPreviewPanel(preview);
      previewIsUsable = preview.overlap === null;
    } catch (error) {
      panel.innerHTML = renderEmptyPreviewPanel();
      message.textContent = error instanceof Error ? error.message : "Could not preview.";
    }
    updateSubmitState();
  }

  for (const input of [startDate, endDate, halfDay]) {
    input.addEventListener("input", () => void refreshPreview());
  }
  reason.addEventListener("input", updateSubmitState);
  main.querySelector("#cancel")!.addEventListener("click", () => navigation.goTo("/"));
  updateSubmitState();

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await apiPost("/api/leaves", {
        start_date: startDate.value,
        end_date: endDate.value,
        half_day: halfDay.checked,
        reason: reason.value,
      });
      navigation.goTo("/");
    } catch (error) {
      message.textContent = error instanceof Error ? error.message : "Could not submit.";
    }
  });
}

export async function initApply(): Promise<void> {
  const me = await drawNav("/apply");
  mountApplyPage(document.getElementById("main")!, me);
}

if (typeof document !== "undefined" && document.body?.dataset.page === "apply") void initApply();
