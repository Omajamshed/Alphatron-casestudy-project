import { apiRequest } from "./client";
import { ReviewRunStatus, SuggestionStatus, UsageSummary, HistoryLog } from "../types";

export async function startReview(versionId: string): Promise<{
  run_id: string;
  thread_id: string;
  status: string;
  message: string;
}> {
  return apiRequest(`/review/versions/${versionId}/review`, {
    method: "POST",
  });
}

export async function getReviewStatus(runId: string): Promise<ReviewRunStatus> {
  return apiRequest<ReviewRunStatus>(`/review/${runId}`);
}

export async function submitDecisions(
  runId: string,
  decisions: Record<string, { status: SuggestionStatus; final_text?: string }>
): Promise<ReviewRunStatus> {
  return apiRequest<ReviewRunStatus>(`/review/${runId}/decisions`, {
    method: "POST",
    body: JSON.stringify({ decisions }),
  });
}

export async function getReviewExports(runId: string): Promise<{
  run_id: string;
  email_draft?: string;
  pdf_download_url?: string;
  docx_download_url?: string;
}> {
  return apiRequest(`/review/${runId}/exports`);
}

export async function getUsageSummary(): Promise<UsageSummary> {
  return apiRequest<UsageSummary>("/usage");
}

export async function getHistoryLogs(): Promise<HistoryLog[]> {
  return apiRequest<HistoryLog[]>("/history");
}
