import React from "react";

export const Disclaimer: React.FC = () => {
  return (
    <footer className="disclaimer-banner">
      <div className="disclaimer-text">
        <span className="disclaimer-icon">⚖️</span>
        <span>
          <strong>Legal Notice:</strong> ContractGuard is an informational analysis tool, not legal advice.
          Outputs do not guarantee legal enforceability and should be reviewed by qualified legal counsel.
        </span>
      </div>
      <div style={{ opacity: 0.7, fontSize: "11px" }}>
        Deterministic Rules + RAG Grounding
      </div>
    </footer>
  );
};
