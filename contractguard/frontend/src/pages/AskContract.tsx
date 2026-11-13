import React, { useState } from "react";
import { askContractQuestion } from "../api/contracts";
import { ChatMessage, Citation } from "../types";
import { CitationChip } from "../components/CitationChip";

interface Props {
  versionId: string;
}

export const AskContract: React.FC<Props> = ({ versionId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      sender: "assistant",
      text: "Hello! I am your ContractGuard Assistant. Ask me anything about this agreement. All answers are grounded strictly in your contract clauses and standard benchmarks with verified [clause, page] citations.",
    },
  ]);
  const [inputQuestion, setInputQuestion] = useState("");
  const [isSending, setIsSending] = useState(false);

  const sampleQuestions = [
    "Can the landlord raise rent during the term?",
    "What is the security deposit amount and return policy?",
    "Does this contract automatically renew?",
    "What are the late fees and notice deadlines?",
    "Is my liability capped or unlimited?",
  ];

  const handleSend = async (questionText?: string) => {
    const q = (questionText || inputQuestion).trim();
    if (!q || isSending) return;

    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      sender: "user",
      text: q,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputQuestion("");
    setIsSending(true);

    try {
      const res = await askContractQuestion(versionId, q);
      const assistantMsg: ChatMessage = {
        id: `a-${Date.now()}`,
        sender: "assistant",
        text: res.answer,
        citations: res.citations,
        tokens: res.tokens,
        seconds: res.seconds,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        sender: "assistant",
        text: `Error: ${err.message || "Failed to process question."}`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 170px)" }}>
      {/* Title */}
      <div style={{ marginBottom: "16px" }}>
        <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#fff", letterSpacing: "-0.02em" }}>
          Ask the Contract
        </h1>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>
          Ground-truth RAG Q&A with verifiable clause & page citations. Out-of-scope queries are strictly refused.
        </p>
      </div>

      {/* Suggested Questions */}
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "16px" }}>
        {sampleQuestions.map((sq) => (
          <button
            key={sq}
            type="button"
            onClick={() => handleSend(sq)}
            style={{
              padding: "5px 12px",
              borderRadius: "20px",
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid var(--glass-border)",
              color: "var(--text-secondary)",
              fontSize: "12px",
              cursor: "pointer",
              transition: "all 0.15s ease",
            }}
          >
            💬 {sq}
          </button>
        ))}
      </div>

      {/* Messages Scroll Area */}
      <div
        className="glass-card"
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          gap: "18px",
          marginBottom: "16px",
        }}
      >
        {messages.map((m) => {
          const isUser = m.sender === "user";
          return (
            <div
              key={m.id}
              style={{
                alignSelf: isUser ? "flex-end" : "flex-start",
                maxWidth: "75%",
                display: "flex",
                flexDirection: "column",
                alignItems: isUser ? "flex-end" : "flex-start",
              }}
            >
              <div
                style={{
                  padding: "12px 18px",
                  borderRadius: isUser ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                  background: isUser
                    ? "linear-gradient(135deg, var(--primary), #4f46e5)"
                    : "rgba(255, 255, 255, 0.06)",
                  border: isUser ? "none" : "1px solid var(--glass-border)",
                  color: "#fff",
                  fontSize: "14px",
                  lineHeight: 1.5,
                  boxShadow: isUser ? "0 4px 14px var(--primary-glow)" : "none",
                }}
              >
                {m.text}

                {/* Citations list if present */}
                {m.citations && m.citations.length > 0 && (
                  <div
                    style={{
                      marginTop: "12px",
                      paddingTop: "8px",
                      borderTop: "1px solid rgba(255, 255, 255, 0.1)",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      flexWrap: "wrap",
                    }}
                  >
                    <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                      Citations:
                    </span>
                    {m.citations.map((c, idx) => (
                      <CitationChip key={idx} citation={c} />
                    ))}
                  </div>
                )}
              </div>

              {/* Latency and token stats */}
              {m.tokens && m.seconds !== undefined && (
                <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
                  {m.seconds}s • {m.tokens.in + m.tokens.out} tokens ({m.tokens.in} in / {m.tokens.out} out)
                </div>
              )}
            </div>
          );
        })}

        {isSending && (
          <div style={{ alignSelf: "flex-start", color: "var(--text-muted)", fontSize: "13px" }}>
            ContractGuard is retrieving contract passages and verifying citations...
          </div>
        )}
      </div>

      {/* Input box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        style={{ display: "flex", gap: "10px" }}
      >
        <input
          type="text"
          className="input-control"
          placeholder="Ask a question about this contract (e.g. Can landlord raise rent?)..."
          value={inputQuestion}
          onChange={(e) => setInputQuestion(e.target.value)}
          disabled={isSending}
        />
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isSending || !inputQuestion.trim()}
          style={{ padding: "0 24px" }}
        >
          {isSending ? "Thinking..." : "Send"}
        </button>
      </form>
    </div>
  );
};
