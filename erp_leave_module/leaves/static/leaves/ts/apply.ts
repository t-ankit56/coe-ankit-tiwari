import type { CurrentUser, LeavePreview } from "./types.js";

export function renderPreviewPanel(preview: LeavePreview): string {
  throw new Error("NotImplementedError");
}

export function mountApplyPage(main: HTMLElement, me: CurrentUser): void {
  throw new Error("NotImplementedError");
}

export async function initApply(): Promise<void> {
  throw new Error("NotImplementedError");
}
