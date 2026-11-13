import React, { useEffect, useState } from "react";
import { getVersionClauses } from "../api/contracts";
import { Clause } from "../types";
import { ClauseCard } from "../components/ClauseCard";

interface Props {
  versionId: string;
}

export const ClauseExplorer: React.FC<Props> = ({ versionId }) => {
  const [clauses, setClauses] = useState<Clause[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [severityFilter, setSeverityFilter] = useState<string>("all");

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await getVersionClauses(versionId);
        setClauses(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [versionId]);

  const filteredClauses = clauses.filter((c) => {
    const matchesSev =
      severityFilter === "all" ||
      c.risk_level.toLowerCase() === severityFilter.toLowerCase();
    const matchesSearch =
      !searchTerm ||
      (c.clause_no && c.clause_no.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (c.heading && c.heading.toLowerCase().includes(searchTerm.toLowerCase())) ||
      c.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (c.summary && c.summary.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesSev && matchesSearch;
  });

  return (
    <div>
      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#fff", letterSpacing: "-0.02em" }}>
          Clause Explorer
        </h1>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>
          Browse all extracted clauses with plain-language summaries and calibrated risk assessments.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div
        className="glass-card"
        style={{
          padding: "16px 20px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "16px",
          marginBottom: "24px",
          flexWrap: "wrap",
        }}
      >
        {/* Search */}
        <div style={{ flex: 1, minWidth: "260px" }}>
          <input
            type="text"
            className="input-control"
            placeholder="Search clauses by keyword, topic, or clause number (e.g. 7.2)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Severity Filter Pills */}
        <div style={{ display: "flex", gap: "6px" }}>
          {["all", "critical", "high", "medium", "low"].map((sev) => (
            <button
              key={sev}
              type="button"
              onClick={() => setSeverityFilter(sev)}
              className="btn"
              style={{
                padding: "6px 12px",
                fontSize: "12px",
                textTransform: "capitalize",
                background:
                  severityFilter === sev
                    ? "rgba(99, 102, 241, 0.3)"
                    : "rgba(255, 255, 255, 0.05)",
                borderColor:
                  severityFilter === sev
                    ? "var(--primary)"
                    : "var(--glass-border)",
                color: severityFilter === sev ? "#fff" : "var(--text-secondary)",
              }}
            >
              {sev === "all" ? "All Clauses" : `${sev} Risk`}
            </button>
          ))}
        </div>
      </div>

      {/* Clause Cards List */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "60px", color: "var(--text-muted)" }}>
          Loading extracted clauses...
        </div>
      ) : filteredClauses.length === 0 ? (
        <div className="glass-card" style={{ textAlign: "center", padding: "40px" }}>
          <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>
            No clauses match your active search and filter criteria.
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {filteredClauses.map((clause) => (
            <ClauseCard key={clause.id} clause={clause} />
          ))}
        </div>
      )}
    </div>
  );
};
