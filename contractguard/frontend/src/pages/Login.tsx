import React, { useState } from "react";

interface Props {
  onLogin: (email: string, pass: string) => Promise<void>;
  onRegister: (email: string, pass: string) => Promise<void>;
}

export const Login: React.FC<Props> = ({ onLogin, onRegister }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (isRegister) {
        await onRegister(email, password);
      } else {
        await onLogin(email, password);
      }
    } catch (err: any) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setError(null);
    setLoading(true);
    try {
      await onLogin("demo@contractguard.local", "demo1234");
    } catch {
      // If demo user doesn't exist yet, register demo user
      try {
        await onRegister("demo@contractguard.local", "demo1234");
      } catch (err: any) {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "80vh",
      }}
    >
      <div className="glass-card" style={{ width: "100%", maxWidth: "420px", padding: "36px" }}>
        <div style={{ textAlign: "center", marginBottom: "28px" }}>
          <div
            style={{
              width: "48px",
              height: "48px",
              borderRadius: "14px",
              background: "linear-gradient(135deg, var(--primary), var(--accent))",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 14px",
              fontSize: "24px",
              boxShadow: "0 8px 24px var(--primary-glow)",
            }}
          >
            🛡️
          </div>
          <h2 style={{ fontSize: "22px", fontWeight: 800, color: "#fff", letterSpacing: "-0.02em" }}>
            ContractGuard
          </h2>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px" }}>
            AI Contract Reviewer & Negotiator
          </p>
        </div>

        {error && (
          <div
            style={{
              padding: "10px 14px",
              borderRadius: "8px",
              background: "rgba(239, 68, 68, 0.15)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              color: "#fca5a5",
              fontSize: "13px",
              marginBottom: "18px",
            }}
          >
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <label style={{ display: "block", fontSize: "12.5px", fontWeight: 600, marginBottom: "6px" }}>
              Email Address
            </label>
            <input
              type="email"
              className="input-control"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@domain.com"
              required
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12.5px", fontWeight: 600, marginBottom: "6px" }}>
              Password
            </label>
            <input
              type="password"
              className="input-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ marginTop: "8px", width: "100%", padding: "11px" }}
          >
            {loading ? "Authenticating..." : isRegister ? "Create Account" : "Sign In"}
          </button>

          <button
            type="button"
            onClick={handleDemoLogin}
            className="btn btn-secondary"
            disabled={loading}
            style={{ width: "100%", padding: "10px", fontSize: "13px" }}
          >
            ⚡ Quick Demo Access (1-Click)
          </button>
        </form>

        <div style={{ textAlign: "center", marginTop: "20px", fontSize: "13px", color: "var(--text-muted)" }}>
          {isRegister ? "Already have an account? " : "Don't have an account? "}
          <button
            type="button"
            onClick={() => setIsRegister(!isRegister)}
            style={{
              background: "none",
              border: "none",
              color: "var(--accent)",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {isRegister ? "Sign In" : "Register"}
          </button>
        </div>
      </div>
    </div>
  );
};
