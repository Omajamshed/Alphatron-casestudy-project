import React, { useState } from "react";
import { uploadContract } from "../api/contracts";
import { Contract } from "../types";

interface Props {
  onUploadSuccess: (contract: Contract) => void;
  onCancel: () => void;
}

export const Upload: React.FC<Props> = ({ onUploadSuccess, onCancel }) => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [contractType, setContractType] = useState("rental");
  const [partyRole, setPartyRole] = useState("tenant");
  const [jurisdiction, setJurisdiction] = useState("US");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      if (!title) {
        setTitle(selected.name.replace(/\.[^/.]+$/, ""));
      }
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selected = e.dataTransfer.files[0];
      setFile(selected);
      if (!title) {
        setTitle(selected.name.replace(/\.[^/.]+$/, ""));
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a contract file to upload.");
      return;
    }
    if (!title.trim()) {
      setError("Please provide a title for this contract.");
      return;
    }

    setIsUploading(true);
    setUploadProgress(25);
    setError(null);

    try {
      setUploadProgress(50);
      const contract = await uploadContract(file, title, contractType, partyRole, jurisdiction);
      setUploadProgress(100);
      setTimeout(() => {
        onUploadSuccess(contract);
      }, 400);
    } catch (err: any) {
      setError(err.message || "Failed to parse and upload contract.");
      setIsUploading(false);
    }
  };

  return (
    <div style={{ maxWidth: "700px", margin: "0 auto" }}>
      <div style={{ marginBottom: "28px" }}>
        <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#fff", letterSpacing: "-0.02em" }}>
          Upload Contract for Review
        </h1>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>
          Upload PDF, DOCX, or TXT agreements. Clauses and key deadlines will be parsed automatically.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="glass-card" style={{ padding: "32px" }}>
        {error && (
          <div
            style={{
              padding: "12px 16px",
              borderRadius: "8px",
              background: "rgba(239, 68, 68, 0.15)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              color: "#fca5a5",
              fontSize: "13.5px",
              marginBottom: "20px",
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {/* Drag and Drop Box */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          style={{
            border: "2px dashed var(--glass-border-focus)",
            borderRadius: "var(--radius-md)",
            padding: "36px 20px",
            textAlign: "center",
            background: "rgba(255, 255, 255, 0.02)",
            cursor: "pointer",
            marginBottom: "24px",
            transition: "all 0.2s ease",
          }}
          onClick={() => document.getElementById("file-input")?.click()}
        >
          <input
            id="file-input"
            type="file"
            accept=".pdf,.docx,.doc,.txt"
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
          <div style={{ fontSize: "42px", marginBottom: "12px" }}>📁</div>
          {file ? (
            <div>
              <div style={{ fontSize: "16px", fontWeight: 700, color: "#fff" }}>{file.name}</div>
              <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
                {(file.size / (1024 * 1024)).toFixed(2)} MB • Click to replace file
              </div>
            </div>
          ) : (
            <div>
              <div style={{ fontSize: "16px", fontWeight: 600, color: "#fff" }}>
                Drag and drop your contract here, or click to browse
              </div>
              <div style={{ fontSize: "12.5px", color: "var(--text-muted)", marginTop: "6px" }}>
                Supports PDF, DOCX, and TXT files up to 15 MB
              </div>
            </div>
          )}
        </div>

        {/* Contract Title */}
        <div style={{ marginBottom: "18px" }}>
          <label style={{ display: "block", fontSize: "13px", fontWeight: 600, marginBottom: "6px" }}>
            Contract Title
          </label>
          <input
            type="text"
            className="input-control"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Skyline Apartments Lease Agreement"
            required
          />
        </div>

        {/* Contract Type & Party Role */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "18px" }}>
          <div>
            <label style={{ display: "block", fontSize: "13px", fontWeight: 600, marginBottom: "6px" }}>
              Contract Type
            </label>
            <select
              className="input-control"
              value={contractType}
              onChange={(e) => {
                const t = e.target.value;
                setContractType(t);
                if (t === "rental") setPartyRole("tenant");
                else if (t === "freelance") setPartyRole("freelancer");
                else if (t === "employment") setPartyRole("employee");
              }}
            >
              <option value="rental">Residential / Commercial Rental</option>
              <option value="freelance">Freelance / Master Services (MSA)</option>
              <option value="employment">Employment Offer Letter</option>
              <option value="other">General Commercial Agreement</option>
            </select>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "13px", fontWeight: 600, marginBottom: "6px" }}>
              Your Role in Agreement
            </label>
            <select
              className="input-control"
              value={partyRole}
              onChange={(e) => setPartyRole(e.target.value)}
            >
              <option value="tenant">Tenant</option>
              <option value="freelancer">Freelancer / Contractor</option>
              <option value="employee">Employee / Candidate</option>
              <option value="client">Client / Employer</option>
              <option value="other">Other Party</option>
            </select>
          </div>
        </div>

        {/* Jurisdiction */}
        <div style={{ marginBottom: "24px" }}>
          <label style={{ display: "block", fontSize: "13px", fontWeight: 600, marginBottom: "6px" }}>
            Governing Jurisdiction (Optional)
          </label>
          <input
            type="text"
            className="input-control"
            value={jurisdiction}
            onChange={(e) => setJurisdiction(e.target.value)}
            placeholder="e.g. California, US or England & Wales"
          />
        </div>

        {/* Ingestion Progress bar */}
        {isUploading && (
          <div style={{ marginBottom: "20px" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontSize: "12px",
                color: "var(--accent)",
                marginBottom: "6px",
              }}
            >
              <span>Parsing document pages & segmenting clauses...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div
              style={{
                width: "100%",
                height: "6px",
                background: "rgba(255, 255, 255, 0.1)",
                borderRadius: "3px",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${uploadProgress}%`,
                  height: "100%",
                  background: "linear-gradient(90deg, var(--primary), var(--accent))",
                  transition: "width 0.3s ease",
                }}
              />
            </div>
          </div>
        )}

        {/* Submit Actions */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px" }}>
          <button
            type="button"
            onClick={onCancel}
            className="btn btn-secondary"
            disabled={isUploading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isUploading || !file}
          >
            {isUploading ? "Processing Contract..." : "Upload & Analyze Contract"}
          </button>
        </div>
      </form>
    </div>
  );
};
