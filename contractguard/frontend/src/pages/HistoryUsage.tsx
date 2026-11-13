import React, { useEffect, useState } from "react";
import { getUsageSummary, getHistoryLogs } from "../api/review";
import { UsageSummary, HistoryLog } from "../types";

export const HistoryUsage: React.FC = () => {
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [logs, setLogs] = useState<HistoryLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [u, l] = await Promise.all([getUsageSummary(), getHistoryLogs()]);
        setUsage(u);
        setLogs(l);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div>
      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#fff", letterSpacing: "-0.02em" }}>
          Usage & Activity History
        </h1>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>
          Transparent tracking of token consumption, latency, and estimated LLM costs.
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px", color: "var(--text-muted)" }}>
          Loading usage data...
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          {/* Top Metric Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
            <div className="glass-card" style={{ padding: "20px" }}>
              <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase" }}>
                Total LLM Calls
              </div>
              <div style={{ fontSize: "28px", fontWeight: 800, color: "#fff", marginTop: "4px" }}>
                {usage?.total_calls || 0}
              </div>
            </div>

            <div className="glass-card" style={{ padding: "20px" }}>
              <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase" }}>
                Total Tokens
              </div>
              <div style={{ fontSize: "28px", fontWeight: 800, color: "var(--accent)", marginTop: "4px" }}>
                {(usage?.total_tokens || 0).toLocaleString()}
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
                {usage?.total_tokens_in.toLocaleString()} in / {usage?.total_tokens_out.toLocaleString()} out
              </div>
            </div>

            <div className="glass-card" style={{ padding: "20px" }}>
              <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase" }}>
                Average Latency
              </div>
              <div style={{ fontSize: "28px", fontWeight: 800, color: "#fff", marginTop: "4px" }}>
                {usage?.avg_latency_ms || 0} ms
              </div>
            </div>

            <div className="glass-card" style={{ padding: "20px" }}>
              <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase" }}>
                Estimated Cost
              </div>
              <div style={{ fontSize: "28px", fontWeight: 800, color: "#10b981", marginTop: "4px" }}>
                ${usage?.total_cost_usd?.toFixed(4) || "0.0000"}
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
                USD benchmark
              </div>
            </div>
          </div>

          {/* Activity Logs Table */}
          <div className="glass-card" style={{ padding: "24px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#fff", marginBottom: "16px" }}>
              Recent Feature Execution Logs
            </h3>

            {logs.length === 0 ? (
              <p style={{ color: "var(--text-muted)", fontSize: "13.5px" }}>No activity logs recorded yet.</p>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
                  <thead>
                    <tr style={{ borderBottom: "1px solid var(--glass-border)", textAlign: "left", color: "var(--text-muted)" }}>
                      <th style={{ padding: "10px 12px" }}>Time</th>
                      <th style={{ padding: "10px 12px" }}>Feature</th>
                      <th style={{ padding: "10px 12px" }}>Tokens In</th>
                      <th style={{ padding: "10px 12px" }}>Tokens Out</th>
                      <th style={{ padding: "10px 12px" }}>Latency</th>
                      <th style={{ padding: "10px 12px" }}>Estimated Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((l) => (
                      <tr key={l.id} style={{ borderBottom: "1px solid rgba(255, 255, 255, 0.04)" }}>
                        <td style={{ padding: "10px 12px", color: "var(--text-secondary)" }}>
                          {l.created_at ? new Date(l.created_at).toLocaleTimeString() : "-"}
                        </td>
                        <td style={{ padding: "10px 12px", fontWeight: 600, color: "#fff" }}>
                          {l.feature}
                        </td>
                        <td style={{ padding: "10px 12px", color: "var(--text-secondary)" }}>
                          {l.tokens_in}
                        </td>
                        <td style={{ padding: "10px 12px", color: "var(--text-secondary)" }}>
                          {l.tokens_out}
                        </td>
                        <td style={{ padding: "10px 12px", color: "var(--text-secondary)" }}>
                          {l.latency_ms} ms
                        </td>
                        <td style={{ padding: "10px 12px", color: "#10b981", fontWeight: 600 }}>
                          ${l.cost_usd.toFixed(5)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
