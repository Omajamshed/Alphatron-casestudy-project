import React, { useState } from "react";
import { useAuth } from "./hooks/useAuth";
import { Contract } from "./types";
import { Dashboard } from "./pages/Dashboard";
import { Upload } from "./pages/Upload";
import { ContractOverview } from "./pages/ContractOverview";
import { ClauseExplorer } from "./pages/ClauseExplorer";
import { AskContract } from "./pages/AskContract";
import { ReviewNegotiate } from "./pages/ReviewNegotiate";
import { Export } from "./pages/Export";
import { VersionCompare } from "./pages/VersionCompare";
import { HistoryUsage } from "./pages/HistoryUsage";
import { Login } from "./pages/Login";
import { Disclaimer } from "./components/Disclaimer";

const NAV_TABS = [
  { id: "Dashboard", label: "Dashboard", icon: "📊" },
  { id: "Upload", label: "Upload Contract", icon: "➕" },
  { id: "Overview", label: "Contract Overview", icon: "📑", requiresContract: true },
  { id: "Clause Explorer", label: "Clause Explorer", icon: "🔍", requiresContract: true },
  { id: "Ask Contract", label: "Ask Contract (RAG)", icon: "💬", requiresContract: true },
  { id: "Review & Negotiate", label: "Review & Negotiate", icon: "⚡", requiresContract: true },
  { id: "Exports", label: "Exports & Email", icon: "📧", requiresRun: true },
  { id: "Version Compare", label: "Version Compare", icon: "🔄", requiresContract: true },
  { id: "History & Usage", label: "Usage & Cost", icon: "📈" },
];

export default function App() {
  const { user, token, loading, login, register, logout } = useAuth();
  const [activeTab, setActiveTab] = useState("Dashboard");
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [activeVersionId, setActiveVersionId] = useState<string>("");
  const [activeRunId, setActiveRunId] = useState<string>("");

  if (loading) {
    return (
      <div style={{ display: "grid", placeItems: "center", minHeight: "100vh", color: "var(--text-muted)" }}>
        Loading ContractGuard...
      </div>
    );
  }

  if (!token && !user) {
    return (
      <>
        <div className="bg-glow-container">
          <div className="glow-orb orb-1" />
          <div className="glow-orb orb-2" />
        </div>
        <Login onLogin={login} onRegister={register} />
      </>
    );
  }

  const handleSelectContract = (c: Contract) => {
    setSelectedContract(c);
    // Set dummy version or actual version ID
    setActiveVersionId(c.id);
    setActiveTab("Overview");
  };

  const handleUploadSuccess = (c: Contract) => {
    setSelectedContract(c);
    setActiveVersionId(c.id);
    setActiveTab("Overview");
  };

  return (
    <>
      {/* Background glow orbs */}
      <div className="bg-glow-container">
        <div className="glow-orb orb-1" />
        <div className="glow-orb orb-2" />
        <div className="glow-orb orb-3" />
      </div>

      <div className="app-container">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="brand-header">
            <div className="brand-logo-icon">🛡️</div>
            <div>
              <div className="brand-title">ContractGuard</div>
              <div className="brand-subtitle">AI Contract Reviewer</div>
            </div>
          </div>

          <nav className="nav-menu">
            {NAV_TABS.map((tab) => {
              const disabled =
                (tab.requiresContract && !selectedContract) ||
                (tab.requiresRun && !activeRunId);

              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => !disabled && setActiveTab(tab.id)}
                  className={`nav-link ${activeTab === tab.id ? "active" : ""}`}
                  style={{ opacity: disabled ? 0.45 : 1, cursor: disabled ? "not-allowed" : "pointer" }}
                  disabled={disabled}
                >
                  <span style={{ fontSize: "16px" }}>{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          <div className="sidebar-footer">
            <div style={{ fontWeight: 600, color: "#fff", marginBottom: "2px" }}>
              {user?.email || "User"}
            </div>
            <button
              type="button"
              onClick={logout}
              style={{
                background: "none",
                border: "none",
                color: "#f87171",
                fontSize: "11.5px",
                cursor: "pointer",
                padding: "2px 0",
              }}
            >
              Sign out
            </button>
          </div>
        </aside>

        {/* Main Content Area */}
        <div className="main-wrapper">
          {/* Top Navbar */}
          <header className="top-navbar">
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              {selectedContract ? (
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>Active Contract:</span>
                  <span style={{ fontSize: "13.5px", fontWeight: 700, color: "#fff" }}>
                    {selectedContract.title}
                  </span>
                  <span
                    style={{
                      fontSize: "11px",
                      background: "rgba(99, 102, 241, 0.2)",
                      color: "#c7d2fe",
                      padding: "2px 6px",
                      borderRadius: "4px",
                    }}
                  >
                    v{selectedContract.current_version}
                  </span>
                </div>
              ) : (
                <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>
                  Select or upload a contract to begin
                </span>
              )}
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <span
                style={{
                  fontSize: "11.5px",
                  color: "#34d399",
                  background: "rgba(16, 185, 129, 0.12)",
                  padding: "4px 10px",
                  borderRadius: "20px",
                  border: "1px solid rgba(16, 185, 129, 0.25)",
                }}
              >
                ● Engine Online
              </span>
            </div>
          </header>

          {/* Page Content View */}
          <main className="content-area">
            {activeTab === "Dashboard" && (
              <Dashboard
                onSelectContract={handleSelectContract}
                onNavigateUpload={() => setActiveTab("Upload")}
              />
            )}

            {activeTab === "Upload" && (
              <Upload
                onUploadSuccess={handleUploadSuccess}
                onCancel={() => setActiveTab("Dashboard")}
              />
            )}

            {activeTab === "Overview" && selectedContract && (
              <ContractOverview
                contract={selectedContract}
                versionId={activeVersionId || selectedContract.id}
                onNavigateTab={(tab) => setActiveTab(tab)}
              />
            )}

            {activeTab === "Clause Explorer" && selectedContract && (
              <ClauseExplorer versionId={activeVersionId || selectedContract.id} />
            )}

            {activeTab === "Ask Contract" && selectedContract && (
              <AskContract versionId={activeVersionId || selectedContract.id} />
            )}

            {activeTab === "Review & Negotiate" && selectedContract && (
              <ReviewNegotiate
                versionId={activeVersionId || selectedContract.id}
                onNavigateExport={(rId) => {
                  setActiveRunId(rId);
                  setActiveTab("Exports");
                }}
              />
            )}

            {activeTab === "Exports" && (
              <Export runId={activeRunId} />
            )}

            {activeTab === "Version Compare" && selectedContract && (
              <VersionCompare
                contractId={selectedContract.id}
                onVersionUploaded={() => {}}
              />
            )}

            {activeTab === "History & Usage" && <HistoryUsage />}
          </main>

          {/* Fixed Footer Legal Disclaimer */}
          <Disclaimer />
        </div>
      </div>
    </>
  );
}
