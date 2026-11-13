import React, { useEffect, useState } from "react";
import { getReviewExports } from "../api/review";

interface Props {
  runId: string;
}

export const Export: React.FC<Props> = ({ runId }) => {
  const [exportsData, setExportsData] = useState<{
    email_draft?: string;
    pdf_download_url?: string;
    docx_download_url?: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await getReviewExports(runId);
        setExportsData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [runId]);

  const handleCopyEmail = () => {
    if (exportsData?.email_draft) {
      navigator.clipboard.writeText(exportsData.email_draft);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#fff", letterSpacing: "-0.02em" }}>
          Negotiation Email & Reports
        </h1>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>
          Outputs generated strictly from your approved counter-clauses. Rejected proposals are omitted.
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px", color: "var(--text-muted)" }}>
          Loading generated exports...
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: "24px" }}>
          {/* Email Preview Card */}
          <div className="glass-card" style={{ padding: "24px" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "16px",
              }}
            >
              <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#fff" }}>
                📧 Ready-to-Send Counter-Offer Email
              </h3>
              <button
                type="button"
                onClick={handleCopyEmail}
                className="btn btn-primary"
                style={{ fontSize: "12.5px", padding: "6px 14px" }}
              >
                {copied ? "✓ Copied!" : "📋 Copy Email"}
              </button>
            </div>

            <pre
              style={{
                background: "rgba(5, 8, 20, 0.6)",
                padding: "16px",
                borderRadius: "8px",
                border: "1px solid var(--glass-border)",
                fontSize: "13px",
                lineHeight: 1.6,
                color: "#e2e8f0",
                fontFamily: "Inter, sans-serif",
                whiteSpace: "pre-wrap",
                maxHeight: "500px",
                overflowY: "auto",
              }}
            >
              {exportsData?.email_draft || "No approved counter-clauses to include in email."}
            </pre>
          </div>

          {/* Download Reports Card */}
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div className="glass-card" style={{ padding: "20px" }}>
              <h3 style={{ fontSize: "15px", fontWeight: 700, color: "#fff", marginBottom: "12px" }}>
                📥 Download Reports
              </h3>
              <p style={{ fontSize: "12.5px", color: "var(--text-secondary)", marginBottom: "16px" }}>
                Download comprehensive negotiation documents to share with landlords, clients, or legal advisors.
              </p>

              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {exportsData?.pdf_download_url ? (
                  <a
                    href={exportsData.pdf_download_url}
                    download
                    className="btn btn-secondary"
                    style={{ textDecoration: "none", width: "100%", justifyContent: "center" }}
                  >
                    📄 Download Executive PDF Report
                  </a>
                ) : (
                  <button className="btn btn-secondary" disabled>
                    PDF Generating...
                  </button>
                )}

                {exportsData?.docx_download_url ? (
                  <a
                    href={exportsData.docx_download_url}
                    download
                    className="btn btn-secondary"
                    style={{ textDecoration: "none", width: "100%", justifyContent: "center" }}
                  >
                    📝 Download Editable DOCX Redline
                  </a>
                ) : (
                  <button className="btn btn-secondary" disabled>
                    DOCX Generating...
                  </button>
                )}
              </div>
            </div>

            {/* Safety badge reminder */}
            <div
              className="glass-card"
              style={{
                padding: "16px",
                background: "rgba(16, 185, 129, 0.05)",
                borderColor: "rgba(16, 185, 129, 0.2)",
              }}
            >
              <div style={{ fontSize: "12px", fontWeight: 700, color: "#6ee7b7", marginBottom: "4px" }}>
                🛡️ Human-in-the-Loop Verified
              </div>
              <p style={{ fontSize: "11.5px", color: "var(--text-secondary)", lineHeight: 1.4 }}>
                Every clause in this export was reviewed and approved by you. The original contract file is preserved untouched.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
