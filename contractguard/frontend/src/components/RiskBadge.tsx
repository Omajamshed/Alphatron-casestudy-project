import React from "react";
import { Severity } from "../types";

interface Props {
  severity: Severity | string;
  size?: "sm" | "md" | "lg";
}

export const RiskBadge: React.FC<Props> = ({ severity, size = "md" }) => {
  const sev = (severity || "low").toLowerCase();

  const getIconAndLabel = () => {
    switch (sev) {
      case "critical":
        return {
          icon: "⚠️",
          label: "CRITICAL RISK",
          cls: "badge-critical",
        };
      case "high":
        return {
          icon: "⛔",
          label: "HIGH RISK",
          cls: "badge-high",
        };
      case "medium":
        return {
          icon: "⚡",
          label: "MODERATE RISK",
          cls: "badge-medium",
        };
      case "low":
      default:
        return {
          icon: "🛡️",
          label: "LOW RISK",
          cls: "badge-low",
        };
    }
  };

  const { icon, label, cls } = getIconAndLabel();
  const fontSize = size === "sm" ? "10.5px" : size === "lg" ? "13px" : "11.5px";
  const padding = size === "sm" ? "2px 8px" : size === "lg" ? "6px 14px" : "4px 10px";

  return (
    <span
      className={`badge ${cls}`}
      style={{ fontSize, padding }}
      role="status"
      aria-label={label}
    >
      <span aria-hidden="true">{icon}</span>
      <span>{label}</span>
    </span>
  );
};
