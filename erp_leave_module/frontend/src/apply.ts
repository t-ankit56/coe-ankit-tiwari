import { apiGet, apiPost, navigation } from "./api.js";
import { formatDayLabel, formatMonthName } from "./dates.js";
import { drawNav } from "./nav.js";
import type { CurrentUser, LeavePreview, MonthUsage, ProbationStatus } from "./types.js";

function describeDays(days: number): string {
  return `${days} working ${days === 1 ? "day" : "days"}`;
}

function describeSuggestion(suggestion: NonNullable<ProbationStatus["suggestion"]>): string {
  return suggestion.half_day
    ? `Use 0.5 day on ${formatDayLabel(suggestion.start_date)}`
    : `Use ${formatDayLabel(suggestion.start_date)} – ${formatDayLabel(suggestion.end_date)}`;
}

function describeRange(preview: LeavePreview): string {
  const first = preview.breakdown[0].date;
  const last = preview.breakdown[preview.breakdown.length - 1].date;
  return first === last ? formatDayLabel(first) : `${formatDayLabel(first)} – ${formatDayLabel(last)}`;
}

function setText(id: string, text: string | number): void {
  document.getElementById(id)!.textContent = String(text);
}

function setHidden(id: string, hidden: boolean): void {
  document.getElementById(id)!.hidden = hidden;
}

function cloneTemplate(id: string): DocumentFragment {
  return (document.getElementById(id) as HTMLTemplateElement).content.cloneNode(true) as DocumentFragment;
}

function setPart(fragment: ParentNode, selector: string, text: string | number): void {
  fragment.querySelectorAll(selector).forEach((element) => {
    element.textContent = String(text);
  });
}

// The preview panel has three versions in apply.html. Show one of them and hide the rest.
function showPreviewVersion(version: "empty" | "result" | "warning"): void {
  setHidden("preview-empty", version !== "empty");
  setHidden("preview-result", version !== "result");
  setHidden("probation-warning", version !== "warning");
  document.getElementById("month-limits")!.replaceChildren();
}

export function showEmptyPreview(): void {
  showPreviewVersion("empty");
}

function buildMonthLimit(month: MonthUsage, limit: number, requestRange: string): DocumentFragment {
  const card = cloneTemplate("month-limit");
  setPart(card, ".month-name", formatMonthName(month.month));
  setPart(card, ".limit", limit);
  setPart(card, ".used", month.used);
  setPart(card, ".limit-left", `${month.left} left`);
  setPart(card, ".request-range", requestRange);
  setPart(card, ".requested", month.requested);
  setPart(card, ".over-days", `${month.over} days over`);
  card.querySelector<HTMLElement>(".meter-fill")!.style.width = `${Math.min(100, (month.used / limit) * 100)}%`;
  card.querySelector(".day-row")!.classList.toggle("day-row-over", month.over > 0);
  card.querySelector<HTMLElement>(".over-line")!.hidden = month.over === 0;
  card.querySelector<HTMLElement>(".within-line")!.hidden = month.over > 0;
  return card;
}

function showProbationWarning(preview: LeavePreview, probation: ProbationStatus): void {
  showPreviewVersion("warning");
  setText("warning-limit", probation.limit);
  const suggestionButton = document.getElementById("use-suggestion") as HTMLButtonElement;
  suggestionButton.hidden = probation.suggestion === null;
  if (probation.suggestion) {
    suggestionButton.textContent = describeSuggestion(probation.suggestion);
    suggestionButton.dataset.start = probation.suggestion.start_date;
    suggestionButton.dataset.end = probation.suggestion.end_date;
    suggestionButton.dataset.half = String(probation.suggestion.half_day);
  }
  const range = describeRange(preview);
  document
    .getElementById("month-limits")!
    .replaceChildren(...probation.months.map((month) => buildMonthLimit(month, probation.limit, range)));
}

function buildCheck(ok: boolean, text: string): DocumentFragment {
  const check = cloneTemplate(ok ? "check-ok" : "check-bad");
  setPart(check, ".check-text", text);
  return check;
}

function showPreviewResult(preview: LeavePreview): void {
  showPreviewVersion("result");
  setText("preview-days", describeDays(preview.days));
  setText("preview-range", `${describeRange(preview)} ${preview.breakdown[preview.breakdown.length - 1].date.slice(0, 4)}`);
  const dayRows = preview.breakdown.map((day) => {
    const row = cloneTemplate("day-row");
    setPart(row, ".day-label", formatDayLabel(day.date));
    setPart(row, ".day-count", day.counts);
    row.querySelector(".day-count")!.classList.toggle("day-count-zero", day.counts === 0);
    const pill = row.querySelector<HTMLElement>(".pill")!;
    pill.hidden = !day.label;
    pill.textContent = day.label ?? "";
    return row;
  });
  document.getElementById("preview-day-rows")!.replaceChildren(...dayRows);
  const checks: DocumentFragment[] = [];
  if (preview.probation === null) {
    checks.push(buildCheck(true, "Personal leave has no yearly limit, so no balance is used."));
  } else {
    for (const month of preview.probation.months) {
      checks.push(
        buildCheck(
          true,
          `Within your probation limit: ${month.used + month.requested} of ${preview.probation.limit} days used in ${formatMonthName(month.month)}.`,
        ),
      );
    }
  }
  checks.push(
    preview.overlap
      ? buildCheck(false, `You already have leave on ${formatDayLabel(preview.overlap.start_date)} – ${formatDayLabel(preview.overlap.end_date)}.`)
      : buildCheck(true, "No overlap with your other requests."),
  );
  document.getElementById("preview-checks")!.replaceChildren(...checks);
}

export function showPreview(preview: LeavePreview): void {
  if (preview.probation !== null && !preview.probation.ok) {
    showProbationWarning(preview, preview.probation);
  } else {
    showPreviewResult(preview);
  }
}

export function mountApplyPage(me: CurrentUser): void {
  setText("type-note", me.on_probation ? "2 days a month while on probation" : "No yearly limit");
  (document.getElementById("approver") as HTMLInputElement).value = me.approver?.name ?? "";
  const form = document.getElementById("apply-form") as HTMLFormElement;
  const startDate = document.querySelector<HTMLInputElement>("#start-date")!;
  const endDate = document.querySelector<HTMLInputElement>("#end-date")!;
  const halfDay = document.querySelector<HTMLInputElement>("#half-day")!;
  const reason = document.querySelector<HTMLTextAreaElement>("#reason")!;
  const submit = document.querySelector<HTMLButtonElement>("#submit")!;
  const message = document.querySelector<HTMLElement>("#message")!;
  const submitHelp = document.querySelector<HTMLElement>("#submit-help")!;
  let previewIsUsable = false;

  function updateSubmitState(): void {
    submit.disabled = !(startDate.value && endDate.value && reason.value.trim() && previewIsUsable);
  }

  async function refreshPreview(): Promise<void> {
    halfDay.disabled = !startDate.value || startDate.value !== endDate.value;
    if (halfDay.disabled) halfDay.checked = false;
    previewIsUsable = false;
    submitHelp.textContent = "";
    startDate.classList.remove("invalid");
    endDate.classList.remove("invalid");
    message.textContent = "";
    if (!startDate.value || !endDate.value) {
      showEmptyPreview();
      updateSubmitState();
      return;
    }
    const query = `start_date=${startDate.value}&end_date=${endDate.value}&half=${halfDay.checked}`;
    try {
      const preview = await apiGet<LeavePreview>(`/api/leaves/preview?${query}`);
      showPreview(preview);
      const overProbationLimit = preview.probation !== null && !preview.probation.ok;
      previewIsUsable = preview.overlap === null && !overProbationLimit;
      submitHelp.textContent = overProbationLimit ? "Change the dates to continue." : "";
      startDate.classList.toggle("invalid", overProbationLimit);
      endDate.classList.toggle("invalid", overProbationLimit);
    } catch (error) {
      showEmptyPreview();
      message.textContent = error instanceof Error ? error.message : "Could not preview.";
    }
    updateSubmitState();
  }

  for (const input of [startDate, endDate, halfDay]) {
    input.addEventListener("input", () => void refreshPreview());
  }
  document.getElementById("use-suggestion")!.addEventListener("click", (event) => {
    const button = event.currentTarget as HTMLElement;
    startDate.value = button.dataset.start!;
    endDate.value = button.dataset.end!;
    halfDay.disabled = false;
    halfDay.checked = button.dataset.half === "true";
    void refreshPreview();
  });
  reason.addEventListener("input", updateSubmitState);
  document.getElementById("cancel")!.addEventListener("click", () => navigation.goTo("/"));
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
  mountApplyPage(me);
}

if (typeof document !== "undefined" && document.body?.dataset.page === "apply") void initApply();
