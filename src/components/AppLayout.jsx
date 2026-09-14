import React from "react";
import { LogOut, ShieldCheck, CircleUserRound } from 'lucide-react';
import Brand from './Brand';
import StatusPill from './StatusPill';
import Background from './Background';

export default function AppLayout({ user, role, onLogout, children }) {
  return (
    <div className="app-shell dashboard-shell">
      <Background />
      <header className="topbar">
        <Brand />
        <div className="topbar-right">
          <StatusPill>Secure session</StatusPill>
          <div className="user-chip"><CircleUserRound size={18} /><span>{user?.email}</span><b>{role}</b></div>
          <button className="icon-btn" title="Sign out" onClick={onLogout}><LogOut size={18} /></button>
        </div>
      </header>
      <main className="dashboard-main">{children}</main>
      <footer className="footer"><span><ShieldCheck size={14} /> Protected examination workflow</span><span>Cloud security control plane</span></footer>
    </div>
  );
}
