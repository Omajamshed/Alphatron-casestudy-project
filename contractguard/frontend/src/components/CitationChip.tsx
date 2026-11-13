import React from "react";
import { Citation } from "../types";

interface Props {
  citation: Citation;
  onClick?: (citation: Citation) => void;
}

export const CitationChip: React.FC<Props> = ({ citation, onClick }) => {
  return (
    <button
      type="button"
      onClick={() => onClick && onClick(citation)}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "4px",
        padding: "3px 8px",
        borderRadius: "6px",
        background: "rgba(99, 102, 241, 0.15)",
        border: "1px solid rgba(99, 102, 241, 0.35)",
        color: "#c7d2fe",
        fontSize: "11.5px",
        fontFamily: "'JetBrains Mono', monospace",
        cursor: "pointer",
        transition: "all 0.15s ease",
      }}
      title={`Referenced: Clause ${citation.clause}, Page ${citation.page}`}
    >
      <span style={{ opacity: 0.7 }}>📄</span>
      <span>
        Clause {citation.clause} (p. {citation.page})
      </span>
    </button>
  );
};
