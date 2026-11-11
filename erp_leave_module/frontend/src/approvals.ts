import { apiGet, apiPost } from "./api.js";
import { formatDateRange, formatShortDate } from "./dates.js";
import { drawNav, initialsOf } from "./nav.js";
import type { WaitingApproval } from "./types.js";

function setText(id: string, text: string | number): void {
  document.getElementById(id)!.textContent = String(text);
}

function dayWord(days: number): string {
  return days === 1 ? "day" : "days";
}

function fillWaitingList(items: WaitingApproval[], selectedId: number | null): void {
  document.getElementById("no-waiting")!.hidden = items.length > 0;
  const template = document.getElementById("waiting-item") as HTMLTemplateElement;
  const rows = items.map((item) => {
    const row = template.content.cloneNode(true) as DocumentFragment;
    const button = row.querySelector<HTMLElement>(".waiting-item")!;
    button.dataset.leaveId = String(item.id);
    button.classList.toggle("selected", item.id === selectedId);
    row.querySelector(".item-initials")!.textContent = initialsOf(item.requester_name);
    row.querySelector(".item-name")!.textContent = item.requester_name;
    row.querySelector(".item-dates")!.textContent = `Personal · ${formatDateRange(item.start_date, item.end_date)}`;
    row.querySelector(".item-days")!.textContent = String(item.days);
    row.querySelector(".item-unit")!.textContent = dayWord(item.days);
    return row;
  });
  document.getElementById("waiting-list")!.replaceChildren(...rows);
}

function fillDecisionPanel(item: WaitingApproval | undefined): void {
  document.getElementById("nothing-to-decide")!.hidden = item !== undefined;
  document.getElementById("decision-details")!.hidden = item === undefined;
  if (!item) return;
  setText("requester-initials", initialsOf(item.requester_name));
  setText("requester-name", item.requester_name);
  setText("requester-email", item.requester_email);
  setText("detail-dates", formatDateRange(item.start_date, item.end_date));
  setText("detail-days", `${item.days} working ${dayWord(item.days)}`);
  setText("detail-reason", item.reason);
  setText("detail-submitted", formatShortDate(item.submitted_at));
  (document.getElementById("decision-comment") as HTMLTextAreaElement).value = "";
  (document.getElementById("reject") as HTMLButtonElement).disabled = true;
  setText("decision-message", "");
}

export async function mountApprovalsPage(): Promise<void> {
  let items = await apiGet<WaitingApproval[]>("/api/approvals");
  let selectedId: number | null = items.length > 0 ? items[0].id : null;
  const comment = document.getElementById("decision-comment") as HTMLTextAreaElement;
  const reject = document.getElementById("reject") as HTMLButtonElement;

  function render(): void {
    fillWaitingList(items, selectedId);
    fillDecisionPanel(items.find((item) => item.id === selectedId));
  }

  async function decide(action: "approve" | "reject", body?: unknown): Promise<void> {
    try {
      await apiPost(`/api/leaves/${selectedId}/${action}`, body);
    } catch (error) {
      setText("decision-message", error instanceof Error ? error.message : "Could not save the decision.");
      return;
    }
    items = await apiGet<WaitingApproval[]>("/api/approvals");
    selectedId = items.length > 0 ? items[0].id : null;
    render();
  }

  comment.addEventListener("input", () => {
    reject.disabled = comment.value.trim() === "";
  });
  document.getElementById("approve")!.addEventListener("click", () => void decide("approve"));
  reject.addEventListener("click", () => void decide("reject", { comment: comment.value }));
  document.getElementById("waiting-list")!.addEventListener("click", (event) => {
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
  await mountApprovalsPage();
}

if (typeof document !== "undefined" && document.body?.dataset.page === "approvals") void initApprovals();
