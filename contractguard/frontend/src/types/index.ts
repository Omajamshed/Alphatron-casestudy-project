export type ContractType = "rental" | "freelance" | "employment" | "other";
export type PartyRole = "tenant" | "freelancer" | "employee" | "client" | "other";
export type Severity = "low" | "medium" | "high" | "critical";
export type SuggestionStatus = "pending" | "approved" | "edited" | "rejected";

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Contract {
  id: string;
  title: string;
  contract_type: ContractType;
  party_role?: PartyRole;
  jurisdiction?: string;
  current_version: number;
  created_at: string;
  latest_risk_score?: number | null;
  next_deadline?: string | null;
  versions_count: number;
}

export interface ContractVersion {
  id: string;
  version: number;
  filename?: string;
  page_count: number;
  risk_score?: number | null;
  uploaded_at?: string;
}

export interface Clause {
  id: string;
  version_id: string;
  clause_no?: string;
  heading?: string;
  text: string;
  page_start: number;
  page_end: number;
  clause_type?: string;
  summary?: string;
  risk_level: Severity;
}

export interface KeyTerm {
  id: string;
  clause_id?: string;
  clause_no?: string;
  kind: string;
  raw_text?: string;
  value_number?: number;
  value_unit?: string;
  value_date?: string;
  computed?: {
    deadline_date?: string;
    trap_date?: string;
    exposure_amount?: number;
    penalty_amount?: number;
    formula?: string;
    warning?: string;
    description?: string;
    confidence?: string;
    is_uncapped?: boolean;
    known_financial_exposure?: number;
  };
}

export interface Finding {
  id: string;
  clause_id: string;
  clause_no?: string;
  heading?: string;
  original_text?: string;
  severity: Severity;
  category: string;
  reason: string;
  standard_term_ref?: string;
  score: number;
}

export interface CategoryBreakdown {
  category: string;
  count: number;
  max_severity: Severity;
  weight: number;
  score_contribution: number;
}

export interface RiskAnalysis {
  version_id: string;
  contract_id: string;
  overall_score: number;
  risk_level: "Low" | "Moderate" | "High" | "Critical";
  findings: Finding[];
  category_breakdown: CategoryBreakdown[];
  total_findings: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
}

export interface Suggestion {
  id: string;
  finding_id: string;
  clause_id?: string;
  clause_no?: string;
  heading?: string;
  original_text: string;
  proposed_text: string;
  rationale: string;
  status: SuggestionStatus;
  final_text?: string | null;
  category?: string;
  severity?: Severity;
}

export interface ReviewRunStatus {
  run_id: string;
  thread_id: string;
  status: "running" | "awaiting_review" | "completed" | "failed";
  suggestions: Suggestion[];
  decisions_count: number;
  pending_count: number;
  total_count: number;
  progress_percentage: number;
  message?: string;
}

export interface Citation {
  file?: string;
  clause: string;
  page: number;
  clause_id?: string;
  heading?: string;
}

export interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  citations?: Citation[];
  tokens?: { in: number; out: number };
  seconds?: number;
}

export interface UsageSummary {
  total_calls: number;
  total_tokens_in: number;
  total_tokens_out: number;
  total_tokens: number;
  total_cost_usd: number;
  avg_latency_ms: number;
  by_feature: Record<string, { calls: number; tokens: number; cost: number }>;
}

export interface HistoryLog {
  id: number;
  feature: string;
  tokens_in: number;
  tokens_out: number;
  latency_ms: number;
  cost_usd: number;
  created_at: string;
}
