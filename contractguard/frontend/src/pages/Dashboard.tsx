import React, { useEffect, useState } from "react";
import { getContracts, deleteContract } from "../api/contracts";
import { Contract } from "../types";
import { RiskBadge } from "../components/RiskBadge";

interface Props {
  onSelectContract: (contract: Contract) => void;
  onNavigateUpload: () => void;
}

export const Dashboard: React.FC<Props> = ({ onSelectContract, onNavigateUpload }) => {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchContractsList = async () => {
    try {
      const data = await getContracts();
      setContracts(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContractsList();
  }, []);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (confirm("Are you sure you want to delete this contract and all derived data?")) {
      await deleteContract(id);
      fetchContractsList();
    }
  };

  return (
    <div>
      {/* Top action bar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "28px",
        }}
      >
        <div>
          <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#fff", letterSpacing: "-0.02em" }}>
            Contract Portfolio
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>
            Overview of uploaded rental agreements, freelance MSAs, and employment offers.
          </p>
        </div>

        <button
          type="button"
          onClick={onNavigateUpload}
          className="btn btn-primary"
          style={{ fontSize: "14px", padding: "10px 20px" }}
        >
          <span>➕</span>
          <span>Upload New Contract</span>
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px", color: "var(--text-muted)" }}>
          Loading your contracts...
        </div>
      ) : contracts.length === 0 ? (
        <div
          className="glass-card"
          style={{
            textAlign: "center",
            padding: "60px 30px",
            border: "1px dashed rgba(255, 255, 255, 0.15)",
          }}
        >
          <div style={{ fontSize: "40px", marginBottom: "16px" }}>📑</div>
          <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#fff", marginBottom: "8px" }}>
            No contracts analyzed yet
          </h3>
          <p
            style={{
              fontSize: "14px",
              color: "var(--text-secondary)",
              maxWidth: "480px",
              margin: "0 auto 24px",
            }}
          >
            Upload your lease, job offer, or client services contract to identify risky clauses,
            calculate exact deadlines, and draft counter-proposals.
          </p>
          <button
            type="button"
            onClick={onNavigateUpload}
            className="btn btn-primary"
          >
            Upload First Contract
          </button>
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
            gap: "20px",
          }}
        >
          {contracts.map((c) => {
            const score = c.latest_risk_score !== undefined && c.latest_risk_score !== null
              ? c.latest_risk_score
              : null;
            const sev =
              score === null
                ? "low"
                : score >= 70
                ? "critical"
                : score >= 50
                ? "high"
                : score >= 25
                ? "medium"
                : "low";

            return (
              <div
                key={c.id}
                onClick={() => onSelectContract(c)}
                className="glass-card"
                style={{
                  cursor: "pointer",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                }}
              >
                <div>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      marginBottom: "12px",
                    }}
                  >
                    <span
                      style={{
                        fontSize: "11px",
                        textTransform: "uppercase",
                        letterSpacing: "0.06em",
                        fontWeight: 700,
                        color: "var(--accent)",
                        background: "rgba(6, 182, 212, 0.12)",
                        padding: "3px 8px",
                        borderRadius: "6px",
                      }}
                    >
                      {c.contract_type} • {c.party_role || "User"}
                    </span>
                    <button
                      type="button"
                      onClick={(e) => handleDelete(e, c.id)}
                      style={{
                        background: "transparent",
                        border: "none",
                        color: "var(--text-muted)",
                        fontSize: "14px",
                        cursor: "pointer",
                        padding: "4px",
                      }}
                      title="Delete contract"
                    >
                      🗑️
                    </button>
                  </div>

                  <h3
                    style={{
                      fontSize: "17px",
                      fontWeight: 700,
                      color: "#fff",
                      marginBottom: "8px",
                      lineHeight: 1.3,
                    }}
                  >
                    {c.title}
                  </h3>

                  <div style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "16px" }}>
                    Version {c.current_version} • Uploaded on {new Date(c.created_at).toLocaleDateString()}
                  </div>
                </div>

                <div
                  style={{
                    paddingTop: "14px",
                    borderTop: "1px solid var(--glass-border)",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div>
                    {score !== null ? (
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span style={{ fontSize: "18px", fontWeight: 800, color: "#fff" }}>
                          {score}
                        </span>
                        <RiskBadge severity={sev} size="sm" />
                      </div>
                    ) : (
                      <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                        Pending Analysis
                      </span>
                    )}
                  </div>

                  {c.next_deadline && (
                    <div
                      style={{
                        fontSize: "11.5px",
                        color: "#f59e0b",
                        background: "rgba(245, 158, 11, 0.1)",
                        padding: "3px 8px",
                        borderRadius: "4px",
                      }}
                    >
                      ⏱️ {c.next_deadline}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
