import React from "react";
import { useReviewRun } from "../hooks/useReviewRun";
import { SuggestionCard } from "../components/SuggestionCard";
import { SuggestionStatus } from "../types";

interface Props {
  versionId: string;
  onNavigateExport: (runId: string) => void;
}

export const ReviewNegotiate: React.FC<Props> = ({ versionId, onNavigateExport }) => {
  const {
    runId,
    reviewStatus,
    loading,
    error,
    startReview,
    makeDecision,
  } = useReviewRun();

  const handleStartAgent = async () => {
    try {
      await startReview(versionId);
    } catch (e) {
      console.error(e);
    }
  };

  const handleDecision = (sId: string, status: SuggestionStatus, finalText?: string) => {
    makeDecision(sId, status, finalText);
  };

  const hasApprovedOrEdited = reviewStatus?.suggestions.some(
    (s) => s.status === "approved" || s.status === "edited"
  );

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "24px",
        }}
      >
        <div>
          <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#fff", letterSpacing: "-0.02em" }}>
            Review & Negotiate
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>
            Human-in-the-loop review agent. Approve, customize, or reject proposed replacement clauses.
          </p>
        </div>

        {runId && (
          <button
            type="button"
            onClick={() => onNavigateExport(runId)}
            className="btn btn-primary"
            disabled={!hasApprovedOrEdited}
            title={
              !hasApprovedOrEdited
                ? "Approve or edit at least one counter-clause before exporting."
                : "Proceed to export email draft and reports"
            }
          >
            📧 View Negotiation Email & Export
          </button>
        )}
      </div>

      {error && (
        <div
          style={{
            padding: "12px 16px",
            borderRadius: "8px",
            background: "rgba(239, 68, 68, 0.15)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            color: "#fca5a5",
            fontSize: "13.5px",
            marginBottom: "20px",
          }}
        >
          ⚠️ {error}
        </div>
      )}

      {!runId && !reviewStatus ? (
        <div
          className="glass-card"
          style={{
            textAlign: "center",
            padding: "60px 30px",
            border: "1px dashed rgba(255, 255, 255, 0.15)",
          }}
        >
          <div style={{ fontSize: "40px", marginBottom: "16px" }}>🤖</div>
          <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#fff", marginBottom: "8px" }}>
            LangGraph Review Agent Ready
          </h3>
          <p
            style={{
              fontSize: "14px",
              color: "var(--text-secondary)",
              maxWidth: "520px",
              margin: "0 auto 24px",
              lineHeight: 1.5,
            }}
          >
            The review agent retrieves standard market terms from the knowledge base, drafts safer
            counter-clauses for every flagged risk, and pauses for your approval.
          </p>
          <button
            type="button"
            onClick={handleStartAgent}
            className="btn btn-primary"
            disabled={loading}
            style={{ padding: "12px 28px", fontSize: "14.5px" }}
          >
            {loading ? "Initializing Review Agent..." : "⚡ Run Review Agent"}
          </button>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Progress Bar Card */}
          <div className="glass-card" style={{ padding: "18px 24px" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "8px",
              }}
            >
              <div>
                <span style={{ fontSize: "14px", fontWeight: 700, color: "#fff" }}>
                  Review Decision Progress:{" "}
                </span>
                <span style={{ fontSize: "14px", color: "var(--accent)" }}>
                  {reviewStatus?.decisions_count} of {reviewStatus?.total_count} Decided
                </span>
              </div>
              <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--primary)" }}>
                {reviewStatus?.progress_percentage}%
              </span>
            </div>

            <div
              style={{
                width: "100%",
                height: "8px",
                background: "rgba(255, 255, 255, 0.08)",
                borderRadius: "4px",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${reviewStatus?.progress_percentage || 0}%`,
                  height: "100%",
                  background: "linear-gradient(90deg, var(--primary), var(--accent))",
                  transition: "width 0.3s ease",
                }}
              />
            </div>
          </div>

          {/* Suggestions List */}
          {reviewStatus && reviewStatus.suggestions.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {reviewStatus.suggestions.map((sug) => (
                <SuggestionCard
                  key={sug.id}
                  suggestion={sug}
                  onDecision={handleDecision}
                />
              ))}
            </div>
          ) : (
            <div className="glass-card" style={{ textAlign: "center", padding: "40px" }}>
              <p style={{ color: "var(--text-muted)" }}>
                {loading ? "Agent is generating counter-clauses..." : "No counter-clauses needed for this contract."}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
