export interface ApiErrorBody {
  error: string;
}

export interface CurrentUser {
  id: number;
  name: string;
  email: string;
  is_approver: boolean;
  on_probation: boolean;
  approver: { name: string } | null;
}

export type LeaveStatus = "pending" | "approved" | "rejected";

export interface Leave {
  id: number;
  start_date: string;
  end_date: string;
  half_day: boolean;
  days: number;
  reason: string;
  status: LeaveStatus;
  approver_name: string;
  decision_comment: string;
  submitted_at: string;
}

export interface WaitingApproval extends Leave {
  requester_name: string;
  requester_email: string;
}

export interface DayInRange {
  date: string;
  counts: number;
  label: string | null;
}

export interface SuggestedRequest {
  start_date: string;
  end_date: string;
  half_day: boolean;
}

export interface MonthUsage {
  month: string;
  used: number;
  requested: number;
  left: number;
  over: number;
}

export interface ProbationStatus {
  ok: boolean;
  limit: number;
  months: MonthUsage[];
  suggestion: SuggestedRequest | null;
}

export interface LeaveOverlap {
  start_date: string;
  end_date: string;
}

export interface LeavePreview {
  days: number;
  breakdown: DayInRange[];
  overlap: LeaveOverlap | null;
  probation: ProbationStatus | null;
}

export interface MyLeavesResponse {
  summary: { days_taken: number; pending_count: number };
  leaves: Leave[];
}
