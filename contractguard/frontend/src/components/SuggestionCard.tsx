import React, { useState } from "react";
import { Suggestion, SuggestionStatus } from "../types";
import { RiskBadge } from "./RiskBadge";

interface Props {
  suggestion: Suggestion;
  onDecision: (suggestionId: string, status: SuggestionStatus, finalText?: string) => void;
}

export const SuggestionCard: React.FC<Props> = ({ suggestion, onDecision }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState(
    suggestion.final_text || suggestion.proposed_text
  );

  const handleSaveEdit = () => {
    setIsEditing(false);
    onDecision(suggestion.id, "edited", editedText);
  };

  return (
    <div
      className="glass-card"
      style={{
        padding: "20px 24px",
        borderColor:
          suggestion.status === "approved"
            ? "rgba(16, 185, 129, 0.4)"
            : suggestion.status === "rejected"
            ? "rgba(100, 116, 139, 0.3)"
            : suggestion.status === "edited"
            ? "rgba(99, 102, 241, 0.4)"
            : "var(--glass-border)",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "14px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: "12px",
              padding: "2px 8px",
              borderRadius: "4px",
              background: "rgba(255, 255, 255, 0.08)",
              color: "#e2e8f0",
              fontWeight: 600,
            }}
          >
            {suggestion.clause_no || "Clause"}
          </span>
          <h4 style={{ fontSize: "15px", fontWeight: 700, color: "#fff" }}>
            {suggestion.heading || "Counter-Clause Proposal"}
          </h4>
          {suggestion.severity && <RiskBadge severity={suggestion.severity} size="sm" />}
        </div>

        {/* Current Decision Badge */}
        <div>
          {suggestion.status === "approved" && (
            <span className="badge badge-low">✓ Approved</span>
          )}
          {suggestion.status === "edited" && (
            <span className="badge" style={{ background: "rgba(99, 102, 241, 0.2)", color: "#a5b4fc", border: "1px solid rgba(99, 102, 241, 0.4)" }}>
              ✎ Custom Edited
            </span>
          )}
          {suggestion.status === "rejected" && (
            <span className="badge" style={{ background: "rgba(100, 116, 139, 0.2)", color: "#94a3b8", border: "1px solid rgba(100, 116, 139, 0.3)" }}>
              ✕ Rejected
            </span>
          )}
          {suggestion.status === "pending" && (
            <span className="badge" style={{ background: "rgba(245, 158, 11, 0.15)", color: "#fbbf24", border: "1px solid rgba(245, 158, 11, 0.3)" }}>
              ⏳ Awaiting Decision
            </span>
          )}
        </div>
      </div>

      {/* Diff comparison view */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "14px",
          marginBottom: "16px",
        }}
      >
        {/* Original Text */}
        <div
          style={{
            padding: "12px 14px",
            borderRadius: "8px",
            background: "rgba(239, 68, 68, 0.06)",
            border: "1px solid rgba(239, 68, 68, 0.2)",
          }}
        >
          <div
            style={{
              fontSize: "11px",
              fontWeight: 700,
              color: "#fca5a5",
              textTransform: "uppercase",
              letterSpacing: "0.04em",
              marginBottom: "6px",
            }}
          >
            Original Contract Language
          </div>
          <div
            style={{
              fontSize: "13px",
              color: "#cbd5e1",
              lineHeight: 1.5,
              whiteSpace: "pre-wrap",
            }}
          >
            {suggestion.original_text}
          </div>
        </div>

        {/* Proposed Replacement */}
        <div
          style={{
            padding: "12px 14px",
            borderRadius: "8px",
            background: "rgba(16, 185, 129, 0.06)",
            border: "1px solid rgba(16, 185, 129, 0.25)",
          }}
        >
          <div
            style={{
              fontSize: "11px",
              fontWeight: 700,
              color: "#6ee7b7",
              textTransform: "uppercase",
              letterSpacing: "0.04em",
              marginBottom: "6px",
              display: "flex",
              justifyContent: "space-between",
            }}
          >
            <span>Proposed Safer Counter-Clause</span>
            {isEditing && <span style={{ color: "var(--accent)" }}>Editing...</span>}
          </div>

          {isEditing ? (
            <div>
              <textarea
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
                rows={5}
                className="input-control"
                style={{ fontSize: "13px", lineHeight: 1.5, marginBottom: "8px" }}
              />
              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  type="button"
                  onClick={handleSaveEdit}
                  className="btn btn-primary"
                  style={{ padding: "6px 12px", fontSize: "12px" }}
                >
                  Save & Apply Edit
                </button>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  className="btn btn-secondary"
                  style={{ padding: "6px 12px", fontSize: "12px" }}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div
              style={{
                fontSize: "13px",
                color: "#f1f5f9",
                lineHeight: 1.5,
                whiteSpace: "pre-wrap",
              }}
            >
              {suggestion.final_text || suggestion.proposed_text}
            </div>
          )}
        </div>
      </div>

      {/* Rationale */}
      <div
        style={{
          background: "rgba(255, 255, 255, 0.03)",
          padding: "10px 14px",
          borderRadius: "6px",
          fontSize: "12.5px",
          color: "var(--text-secondary)",
          marginBottom: "16px",
          borderLeft: "3px solid var(--accent)",
        }}
      >
        <span style={{ fontWeight: 600, color: "var(--accent)" }}>Why this change matters: </span>
        {suggestion.rationale}
      </div>

      {/* Decision Buttons */}
      <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
        <button
          type="button"
          onClick={() => onDecision(suggestion.id, "approved")}
          className={`btn ${suggestion.status === "approved" ? "btn-success" : "btn-secondary"}`}
          style={{ fontSize: "13px" }}
        >
          ✓ Approve Proposal
        </button>
        <button
          type="button"
          onClick={() => setIsEditing(!isEditing)}
          className={`btn ${suggestion.status === "edited" ? "btn-primary" : "btn-secondary"}`}
          style={{ fontSize: "13px" }}
        >
          ✎ Custom Edit
        </button>
        <button
          type="button"
          onClick={() => onDecision(suggestion.id, "rejected")}
          className={`btn ${suggestion.status === "rejected" ? "btn-danger" : "btn-secondary"}`}
          style={{ fontSize: "13px" }}
        >
          ✕ Reject
        </button>
      </div>
    </div>
  );
};
