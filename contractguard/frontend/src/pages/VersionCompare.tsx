import React, { useEffect, useState } from "react";
import { getRiskHistory, uploadVersion } from "../api/contracts";
import { RiskBadge } from "../components/RiskBadge";

interface Props {
  contractId: string;
  onVersionUploaded: () => void;
}

export const VersionCompare: React.FC<Props> = ({ contractId, onVersionUploaded }) => {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [newVersionFile, setNewVersionFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await getRiskHistory(contractId);
      setHistory(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [contractId]);

  const handleUploadNewVersion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newVersionFile) return;

    setUploading(true);
    try {
      await uploadVersion(contractId, newVersionFile);
      setNewVersionFile(null);
      await loadHistory();
      onVersionUploaded();
    } catch (err: any) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#fff", letterSpacing: "-0.02em" }}>
          Version Comparison & Risk History
        </h1>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>
          Track how your risk score changes between negotiation rounds as counter-proposals are adopted.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: "24px" }}>
        {/* Version History Table Card */}
        <div className="glass-card" style={{ padding: "24px" }}>
          <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#fff", marginBottom: "16px" }}>
            📈 Risk Score Trend Across Iterations
          </h3>

          {loading ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
              Loading history...
            </div>
          ) : history.length === 0 ? (
            <p style={{ color: "var(--text-muted)", fontSize: "13.5px" }}>No version history recorded.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {history.map((h, idx) => {
                const prev = idx > 0 ? history[idx - 1] : null;
                const scoreDiff = prev && h.risk_score && prev.risk_score ? h.risk_score - prev.risk_score : 0;

                return (
                  <div
                    key={h.version_id}
                    style={{
                      padding: "16px 20px",
                      borderRadius: "10px",
                      background: "rgba(255, 255, 255, 0.03)",
                      border: "1px solid var(--glass-border)",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <span
                          style={{
                            fontSize: "12px",
                            fontWeight: 700,
                            padding: "2px 8px",
                            borderRadius: "4px",
                            background: "rgba(99, 102, 241, 0.2)",
                            color: "#c7d2fe",
                          }}
                        >
                          Version {h.version}
                        </span>
                        <span style={{ fontSize: "14px", fontWeight: 600, color: "#fff" }}>
                          {h.filename || "Uploaded Contract"}
                        </span>
                      </div>
                      <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
                        Uploaded: {h.uploaded_at ? new Date(h.uploaded_at).toLocaleString() : "Initial"}
                      </div>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                      {h.risk_score !== null ? (
                        <div style={{ textAlign: "right" }}>
                          <div style={{ fontSize: "18px", fontWeight: 800, color: "#fff" }}>
                            {h.risk_score} / 100
                          </div>
                          {scoreDiff !== 0 && (
                            <span
                              style={{
                                fontSize: "11px",
                                fontWeight: 600,
                                color: scoreDiff < 0 ? "#10b981" : "#ef4444",
                              }}
                            >
                              {scoreDiff < 0 ? `▼ ${Math.abs(scoreDiff).toFixed(1)} lower risk` : `▲ ${scoreDiff.toFixed(1)} increased risk`}
                            </span>
                          )}
                        </div>
                      ) : (
                        <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>Unscored</span>
                      )}

                      {h.risk_score !== null && (
                        <RiskBadge
                          severity={
                            h.risk_score >= 70
                              ? "critical"
                              : h.risk_score >= 50
                              ? "high"
                              : h.risk_score >= 25
                              ? "medium"
                              : "low"
                          }
                          size="sm"
                        />
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Upload Revised Version Box */}
        <div className="glass-card" style={{ padding: "24px" }}>
          <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#fff", marginBottom: "12px" }}>
            📤 Upload Revised Draft
          </h3>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "18px", lineHeight: 1.5 }}>
            Received a revised contract draft from the landlord or client? Upload it to compare clause changes and see risk reduction.
          </p>

          <form onSubmit={handleUploadNewVersion}>
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(e) => setNewVersionFile(e.target.files ? e.target.files[0] : null)}
              className="input-control"
              style={{ marginBottom: "14px" }}
              required
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={uploading || !newVersionFile}
              style={{ width: "100%" }}
            >
              {uploading ? "Analyzing Revised Draft..." : "Upload Version"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
