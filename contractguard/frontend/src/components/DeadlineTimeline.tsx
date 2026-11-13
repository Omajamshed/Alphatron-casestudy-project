import React, { useState } from "react";
import { KeyTerm } from "../types";

interface Props {
  keyTerms: KeyTerm[];
}

export const DeadlineTimeline: React.FC<Props> = ({ keyTerms }) => {
  const [activePopover, setActivePopover] = useState<string | null>(null);

  // Filter deadline and calculated terms
  const timelineItems = keyTerms.filter(
    (kt) =>
      kt.kind.includes("date") ||
      kt.kind.includes("deadline") ||
      kt.kind.includes("trap") ||
      kt.kind.includes("period")
  );

  return (
    <div className="glass-card" style={{ padding: "20px 24px" }}>
      <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#fff", marginBottom: "16px" }}>
        📅 Key Dates & Deadline Timeline
      </h3>

      {timelineItems.length === 0 ? (
        <p style={{ fontSize: "13px", color: "var(--text-muted)" }}>
          No critical deadline terms extracted for this contract.
        </p>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "16px" }}>
          {timelineItems.map((item) => {
            const isTrap = item.kind.includes("trap");
            const isNotice = item.kind.includes("notice");
            const hasFormula = item.computed && item.computed.formula;
            const popoverOpen = activePopover === item.id;

            return (
              <div
                key={item.id}
                style={{
                  padding: "14px 16px",
                  borderRadius: "10px",
                  background: isTrap
                    ? "rgba(239, 68, 68, 0.08)"
                    : isNotice
                    ? "rgba(245, 158, 11, 0.08)"
                    : "rgba(255, 255, 255, 0.04)",
                  border: isTrap
                    ? "1px solid rgba(239, 68, 68, 0.3)"
                    : isNotice
                    ? "1px solid rgba(245, 158, 11, 0.3)"
                    : "1px solid var(--glass-border)",
                  position: "relative",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <span
                    style={{
                      fontSize: "11px",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                      fontWeight: 600,
                      color: isTrap ? "#fca5a5" : isNotice ? "#fcd34d" : "var(--text-secondary)",
                    }}
                  >
                    {item.kind.replace("computed_", "").replace(/_/g, " ")}
                  </span>
                  {hasFormula && (
                    <button
                      type="button"
                      onClick={() => setActivePopover(popoverOpen ? null : item.id)}
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
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                      title="How was this calculated?"
                    >
                      ?
                    </button>
                  )}
                </div>

                <div style={{ fontSize: "16px", fontWeight: 700, color: "#fff", marginTop: "6px" }}>
                  {item.value_date ||
                    (item.computed && (item.computed.deadline_date || item.computed.trap_date)) ||
                    item.raw_text ||
                    (item.value_number !== undefined ? `${item.value_number} ${item.value_unit || ""}` : "Noted")}
                </div>

                {item.clause_no && (
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
                    Source: Clause {item.clause_no}
                  </div>
                )}

                {/* "How was this calculated" Popover */}
                {popoverOpen && item.computed && (
                  <div
                    style={{
                      position: "absolute",
                      bottom: "105%",
                      left: "50%",
                      transform: "translateX(-50%)",
                      width: "280px",
                      background: "#0f172a",
                      border: "1px solid var(--primary)",
                      borderRadius: "8px",
                      padding: "12px",
                      boxShadow: "0 10px 25px rgba(0, 0, 0, 0.5)",
                      zIndex: 20,
                      fontSize: "12px",
                      color: "#e2e8f0",
                    }}
                  >
                    <div style={{ fontWeight: 700, color: "var(--accent)", marginBottom: "4px" }}>
                      🧮 Calculation Method:
                    </div>
                    <div
                      style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        background: "rgba(0, 0, 0, 0.4)",
                        padding: "6px",
                        borderRadius: "4px",
                        color: "#38bdf8",
                        marginBottom: "6px",
                        wordBreak: "break-all",
                      }}
                    >
                      {item.computed.formula || "Extracted via pattern matching"}
                    </div>
                    {item.computed.warning && (
                      <div style={{ color: "#fca5a5", fontSize: "11px" }}>
                        ⚠️ {item.computed.warning}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
