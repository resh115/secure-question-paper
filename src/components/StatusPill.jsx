import React from "react";
export default function StatusPill({ children, tone = 'success' }) {
  return <span className={`status-pill ${tone}`}><span className="status-dot" />{children}</span>;
}
