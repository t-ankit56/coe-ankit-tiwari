import type { WaitingApproval } from "./types.js";

export function renderWaitingList(items: WaitingApproval[], selectedId: number | null): string {
  return '<p class="empty">No requests waiting</p>';
}

export function renderDecisionPanel(item: WaitingApproval): string {
  throw new Error("NotImplementedError");
}

export async function mountApprovalsPage(main: HTMLElement): Promise<void> {
  throw new Error("NotImplementedError");
}

export async function initApprovals(): Promise<void> {
  throw new Error("NotImplementedError");
}
