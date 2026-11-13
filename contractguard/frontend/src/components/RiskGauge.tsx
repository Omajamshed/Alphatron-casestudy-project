import React from "react";

interface Props {
  score: number; // 0 to 100
  size?: number;
  label?: string;
}

export const RiskGauge: React.FC<Props> = ({ score, size = 180, label = "Risk Score" }) => {
  const clampedScore = Math.max(0, Math.min(100, Math.round(score)));
  const radius = size * 0.38;
  const strokeWidth = size * 0.08;
  const center = size / 2;
  const circumference = 2 * Math.PI * radius;
  // Use a 270 degree arc gauge
  const arcLength = circumference * 0.75;
  const strokeDashoffset = arcLength - (arcLength * clampedScore) / 100;

  let color = "#10b981"; // Low (green)
  let statusText = "LOW RISK";
  if (clampedScore >= 70) {
    color = "#ef4444"; // Critical (red)
    statusText = "CRITICAL RISK";
  } else if (clampedScore >= 50) {
    color = "#f97316"; // High (orange)
    statusText = "HIGH RISK";
  } else if (clampedScore >= 25) {
    color = "#f59e0b"; // Medium (amber)
    statusText = "MODERATE RISK";
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", position: "relative" }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="40%" stopColor="#f59e0b" />
            <stop offset="70%" stopColor="#f97316" />
            <stop offset="100%" stopColor="#ef4444" />
          </linearGradient>
        </defs>

        {/* Background track */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(255, 255, 255, 0.08)"
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeLinecap="round"
          transform={`rotate(135 ${center} ${center})`}
        />

        {/* Value arc */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform={`rotate(135 ${center} ${center})`}
          style={{ transition: "stroke-dashoffset 0.8s ease, stroke 0.4s ease" }}
        />
      </svg>

      {/* Centered label */}
      <div
        style={{
          position: "absolute",
          top: "46%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          textAlign: "center",
        }}
      >
        <span style={{ fontSize: size * 0.22, fontWeight: 800, color: "#fff", lineHeight: 1 }}>
          {clampedScore}
        </span>
        <span style={{ fontSize: size * 0.09, color: "var(--text-muted)", display: "block" }}>
          / 100
        </span>
        <span
          style={{
            fontSize: size * 0.075,
            fontWeight: 700,
            color,
            marginTop: 4,
            display: "inline-block",
            letterSpacing: "0.04em",
          }}
        >
          {statusText}
        </span>
      </div>

      <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: -6 }}>
        {label}
      </div>
    </div>
  );
};
