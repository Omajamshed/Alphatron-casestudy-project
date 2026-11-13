import React, { useState } from "react";
import { Clause } from "../types";
import { RiskBadge } from "./RiskBadge";

interface Props {
  clause: Clause;
  isHighlighted?: boolean;
}

export const ClauseCard: React.FC<Props> = ({ clause, isHighlighted = false }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className="glass-card"
      id={`clause-${clause.clause_no?.replace(".", "-")}`}
      style={{
        padding: "16px 20px",
        borderColor: isHighlighted ? "var(--primary)" : "var(--glass-border)",
        boxShadow: isHighlighted ? "0 0 16px var(--primary-glow)" : "none",
        transition: "all 0.25s ease",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "10px",
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
            {clause.clause_no || "General"}
          </span>
          <h4 style={{ fontSize: "15px", fontWeight: 600, color: "#fff" }}>
            {clause.heading || "Agreement Term"}
          </h4>
          <span
            style={{
              fontSize: "11px",
              color: "var(--text-muted)",
              background: "rgba(255, 255, 255, 0.04)",
              padding: "2px 6px",
              borderRadius: "4px",
            }}
          >
            p. {clause.page_start}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {clause.clause_type && (
            <span
              style={{
                fontSize: "11px",
                color: "var(--accent)",
                background: "rgba(6, 182, 212, 0.1)",
                padding: "2px 8px",
                borderRadius: "10px",
                textTransform: "capitalize",
              }}
            >
              {clause.clause_type.replace("_", " ")}
            </span>
          )}
          <RiskBadge severity={clause.risk_level} size="sm" />
        </div>
      </div>

      {clause.summary && (
        <p style={{ fontSize: "13.5px", color: "var(--text-secondary)", marginBottom: "12px", lineHeight: 1.5 }}>
          {clause.summary}
        </p>
      )}

      <div>
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          style={{
            background: "transparent",
            border: "none",
            color: "var(--primary)",
            fontSize: "12px",
            fontWeight: 600,
            cursor: "pointer",
            display: "inline-flex",
            alignItems: "center",
            gap: "4px",
            padding: "2px 0",
          }}
        >
          <span>{expanded ? "Hide Original Contract Text ▲" : "View Original Contract Text ▼"}</span>
        </button>

        {expanded && (
          <div
            style={{
              marginTop: "10px",
              padding: "12px",
              borderRadius: "8px",
              background: "rgba(5, 8, 20, 0.6)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              fontSize: "12.5px",
              color: "#cbd5e1",
              whiteSpace: "pre-wrap",
              fontFamily: "'JetBrains Mono', monospace",
              maxHeight: "240px",
              overflowY: "auto",
            }}
          >
            {clause.text}
          </div>
        )}
      </div>
    </div>
  );
};
