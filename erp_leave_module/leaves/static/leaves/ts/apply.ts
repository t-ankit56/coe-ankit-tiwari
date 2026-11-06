import { apiGet, apiPost, navigation } from "./api.js";
import { escapeHtml } from "./html.js";
import { drawNav } from "./nav.js";
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
    <p id="message" class="error"></p>
  </form>
  <section id="preview-panel"></section>`;
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
      panel.innerHTML = "";
      updateSubmitState();
      return;
    }
    const query = `start_date=${startDate.value}&end_date=${endDate.value}&half=${halfDay.checked}`;
    try {
      const preview = await apiGet<LeavePreview>(`/api/leaves/preview?${query}`);
      panel.innerHTML = renderPreviewPanel(preview);
      if (preview.overlap) {
        message.textContent = `You already have leave on ${preview.overlap.start_date} to ${preview.overlap.end_date}.`;
      }
      previewIsUsable = preview.overlap === null;
    } catch (error) {
      panel.innerHTML = "";
      message.textContent = error instanceof Error ? error.message : "Could not preview.";
    }
    updateSubmitState();
  }

  for (const input of [startDate, endDate, halfDay]) {
    input.addEventListener("input", () => void refreshPreview());
  }
  reason.addEventListener("input", updateSubmitState);
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
