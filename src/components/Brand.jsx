import React from "react";
import { ShieldCheck } from 'lucide-react';

export default function Brand({ compact = false }) {
  return (
    <div className={`brand ${compact ? 'brand-compact' : ''}`}>
      <div className="brand-mark"><ShieldCheck size={compact ? 19 : 23} /></div>
      <div>
        <strong>SecurePaper</strong>
        {!compact && <span>Cloud Question-Paper Control</span>}
      </div>
    </div>
  );
}
