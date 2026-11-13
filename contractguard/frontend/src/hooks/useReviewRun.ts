import { useState, useEffect } from "react";
import { getReviewStatus, submitDecisions, startReview } from "../api/review";
import { ReviewRunStatus, SuggestionStatus } from "../types";

export function useReviewRun(initialRunId?: string) {
  const [runId, setRunId] = useState<string | undefined>(initialRunId);
  const [reviewStatus, setReviewStatus] = useState<ReviewRunStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshStatus = async (idToFetch?: string) => {
    const targetId = idToFetch || runId;
    if (!targetId) return;

    setLoading(true);
    try {
      const res = await getReviewStatus(targetId);
      setReviewStatus(res);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to fetch review status");
    } finally {
      setLoading(false);
    }
  };

  const handleStartReview = async (versionId: string) => {
    setLoading(true);
    try {
      const startRes = await startReview(versionId);
      setRunId(startRes.run_id);
      await refreshStatus(startRes.run_id);
      return startRes.run_id;
    } catch (err: any) {
      setError(err.message || "Failed to start review run");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleMakeDecision = async (
    suggestionId: string,
    status: SuggestionStatus,
    finalText?: string
  ) => {
    if (!runId || !reviewStatus) return;

    const currentDecisions: Record<string, { status: SuggestionStatus; final_text?: string }> = {};
    reviewStatus.suggestions.forEach((s) => {
      if (s.id === suggestionId) {
        currentDecisions[s.id] = { status, final_text: finalText || s.proposed_text };
      } else {
        currentDecisions[s.id] = { status: s.status, final_text: s.final_text || s.proposed_text };
      }
    });

    try {
      const updated = await submitDecisions(runId, currentDecisions);
      setReviewStatus(updated);
    } catch (err: any) {
      setError(err.message || "Failed to submit decision");
    }
  };

  useEffect(() => {
    if (runId) {
      refreshStatus(runId);
    }
  }, [runId]);

  return {
    runId,
    reviewStatus,
    loading,
    error,
    refreshStatus,
    startReview: handleStartReview,
    makeDecision: handleMakeDecision,
    setRunId,
  };
}
