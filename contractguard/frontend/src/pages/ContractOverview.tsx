import React, { useEffect, useState } from "react";
import { getVersionRisk, getVersionKeyTerms } from "../api/contracts";
import { Contract, RiskAnalysis, KeyTerm } from "../types";
import { RiskGauge } from "../components/RiskGauge";
import { RiskBadge } from "../components/RiskBadge";
import { DeadlineTimeline } from "../components/DeadlineTimeline";

interface Props {
  contract: Contract;
  versionId: string;
  onNavigateTab: (tab: string) => void;
}

export const ContractOverview: React.FC<Props> = ({ contract, versionId, onNavigateTab }) => {
  const [riskData, setRiskData] = useState<RiskAnalysis | null>(null);
  const [keyTerms, setKeyTerms] = useState<KeyTerm[]>([]);
  const [loading, setLoading] = useState(true);
  const [exposurePopover, setExposurePopover] = useState(false);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [risk, terms] = await Promise.all([
          getVersionRisk(versionId),
          getVersionKeyTerms(versionId),
        ]);
        setRiskData(risk);
        setKeyTerms(terms);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [versionId]);

  // Find computed exposure term
  const exposureTerm = keyTerms.find((t) => t.kind === "computed_financial_exposure");

  return (
    <div>
      {/* Contract Title & Actions */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "28px",
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
            <span
              style={{
                fontSize: "11px",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                fontWeight: 700,
                color: "var(--accent)",
                background: "rgba(6, 182, 212, 0.12)",
                padding: "2px 8px",
                borderRadius: "4px",
              }}
            >
              {contract.contract_type} • Version {contract.current_version}
            </span>
            <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
              Role: {contract.party_role || "User"}
            </span>
          </div>
          <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#fff", letterSpacing: "-0.02em" }}>
            {contract.title}
          </h1>
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <button
            type="button"
            onClick={() => onNavigateTab("Review & Negotiate")}
            className="btn btn-primary"
            style={{ fontSize: "13.5px" }}
          >
            ⚡ Start Review Agent
          </button>
          <button
            type="button"
            onClick={() => onNavigateTab("Ask Contract")}
            className="btn btn-secondary"
            style={{ fontSize: "13.5px" }}
          >
            💬 Ask Questions
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px", color: "var(--text-muted)" }}>
          Loading contract intelligence...
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          {/* Top Metric Cards Grid */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "260px 1fr 300px",
              gap: "20px",
            }}
          >
            {/* Risk Score Gauge Card */}
            <div
              className="glass-card"
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                padding: "20px",
              }}
            >
              <RiskGauge score={riskData?.overall_score || 0} size={190} label="Contract Risk Score" />
            </div>

            {/* Risk Category Breakdown Card */}
            <div className="glass-card" style={{ padding: "22px 26px" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "16px",
                }}
              >
                <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#fff" }}>
                  Risk Category Breakdown
                </h3>
                <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                  {riskData?.total_findings || 0} flagged clauses
                </span>
              </div>

              {riskData && riskData.category_breakdown.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                  {riskData.category_breakdown.map((cat) => (
                    <div key={cat.category}>
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          fontSize: "12.5px",
                          marginBottom: "4px",
                        }}
                      >
                        <span style={{ fontWeight: 600, color: "#e2e8f0", textTransform: "capitalize" }}>
                          {cat.category.replace(/_/g, " ")} ({cat.count})
                        </span>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <RiskBadge severity={cat.max_severity} size="sm" />
                          <span style={{ color: "var(--text-muted)", fontSize: "11.5px" }}>
                            Weight: {cat.weight}x
                          </span>
                        </div>
                      </div>
                      <div
                        style={{
                          width: "100%",
                          height: "6px",
                          background: "rgba(255, 255, 255, 0.08)",
                          borderRadius: "3px",
                          overflow: "hidden",
                        }}
                      >
                        <div
                          style={{
                            width: `${Math.min(100, (cat.score_contribution / 30) * 100)}%`,
                            height: "100%",
                            background:
                              cat.max_severity === "critical"
                                ? "var(--risk-critical)"
                                : cat.max_severity === "high"
                                ? "var(--risk-high)"
                                : "var(--risk-medium)",
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ fontSize: "13px", color: "var(--text-muted)", padding: "20px 0" }}>
                  No high-risk categories identified in this document.
                </div>
              )}
            </div>

            {/* Total Financial Exposure Card */}
            <div className="glass-card" style={{ padding: "22px 24px", position: "relative" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "8px",
                }}
              >
                <span
                  style={{
                    fontSize: "11px",
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    color: "var(--text-secondary)",
                  }}
                >
                  Potential Exposure
                </span>
                {exposureTerm?.computed && (
                  <button
                    type="button"
                    onClick={() => setExposurePopover(!exposurePopover)}
                    style={{
                      background: "rgba(255, 255, 255, 0.1)",
                      border: "none",
                      borderRadius: "50%",
                      width: "18px",
                      height: "18px",
                      color: "#fff",
                      fontSize: "11px",
                      fontWeight: 700,
                      cursor: "pointer",
                    }}
                    title="How was this calculated?"
                  >
                    ?
                  </button>
                )}
              </div>

              <div
                style={{
                  fontSize: "26px",
                  fontWeight: 800,
                  color: exposureTerm?.computed?.is_uncapped ? "#f87171" : "#fff",
                }}
              >
                {exposureTerm?.value_number !== undefined
                  ? `$${exposureTerm.value_number.toLocaleString()}`
                  : "$0"}
                {exposureTerm?.computed?.is_uncapped && " + ∞"}
              </div>

              {exposureTerm?.computed?.is_uncapped ? (
                <div style={{ fontSize: "12px", color: "#fca5a5", marginTop: "6px" }}>
                  ⚠️ Unlimited liability clause flagged. Potential financial loss is uncapped.
                </div>
              ) : (
                <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "6px" }}>
                  Sum of deposit at risk, early termination fees, and late penalties.
                </div>
              )}

              {/* Exposure calculation popover */}
              {exposurePopover && exposureTerm?.computed && (
                <div
                  style={{
                    position: "absolute",
                    top: "100%",
                    right: 0,
                    width: "280px",
                    background: "#0f172a",
                    border: "1px solid var(--primary)",
                    borderRadius: "8px",
                    padding: "12px",
                    boxShadow: "0 10px 25px rgba(0, 0, 0, 0.6)",
                    zIndex: 30,
                    fontSize: "12px",
                    color: "#e2e8f0",
                    marginTop: "8px",
                  }}
                >
                  <div style={{ fontWeight: 700, color: "var(--accent)", marginBottom: "4px" }}>
                    🧮 Exposure Formula:
                  </div>
                  <div
                    style={{
                      fontFamily: "'JetBrains Mono', monospace",
                      background: "rgba(0, 0, 0, 0.4)",
                      padding: "6px",
                      borderRadius: "4px",
                      color: "#38bdf8",
                    }}
                  >
                    {exposureTerm.computed.formula}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Key Dates Timeline */}
          <DeadlineTimeline keyTerms={keyTerms} />
        </div>
      )}
    </div>
  );
};
