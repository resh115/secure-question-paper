import React from "react";
import { useState } from "react";
import {
  LockKeyhole,
  Mail,
  ArrowRight,
  ShieldCheck,
  Fingerprint,
  Cloud,
  Eye,
  EyeOff,
} from "lucide-react";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../lib/firebase";
import Brand from "../components/Brand";
import Background from "../components/Background";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();

    setBusy(true);
    setError("");

    try {
      const credential = await signInWithEmailAndPassword(
        auth,
        email.trim(),
        password
      );

      await onLogin(credential.user);
    } catch (err) {
      setError(
        err?.message?.replace("Firebase: ", "") ||
          "Unable to sign in."
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-shell login-shell">
      <Background />

      <header className="topbar login-topbar">
        <Brand />
      </header>

      <main className="login-main">
        <section className="login-visual">
          <div className="eyebrow">
            <ShieldCheck size={15} />
            ZERO-TRUST EXAM CONTROL
          </div>

          <h1>
            Protect the paper.
            <br />
            <span>Control the moment.</span>
          </h1>

          <p>
            Encrypted question papers remain locked until an
            authorized examination release. Every sensitive
            action is authenticated, role-controlled and audited.
          </p>

          <div className="security-stack">
            <div>
              <Fingerprint size={18} />
              <span>Firebase identity</span>
              <b>Verified</b>
            </div>

            <div>
              <LockKeyhole size={18} />
              <span>AES-256-GCM</span>
              <b>Active</b>
            </div>

            <div>
              <Cloud size={18} />
              <span>Multi-cloud storage</span>
              <b>Connected</b>
            </div>
          </div>
        </section>

        <section className="login-card glass-card">
          <div className="card-kicker">SECURE ACCESS</div>

          <h2>Sign in</h2>

          <p className="muted">
            Use your authorized examination account.
          </p>

          <form onSubmit={submit}>
            <label>Email address</label>

            <div className="input-wrap">
              <Mail size={18} />

              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>

            <label>Password</label>

            <div className="input-wrap password-input-wrap">
              <LockKeyhole size={18} />

              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword((prev) => !prev)}
                aria-label={
                  showPassword
                    ? "Hide password"
                    : "Show password"
                }
                title={
                  showPassword
                    ? "Hide password"
                    : "Show password"
                }
              >
                {showPassword ? (
                  <Eye size={17} />
                ) : (
                  <EyeOff size={17} />
                )}
              </button>
            </div>

            {error && (
              <div className="error-box">
                {error}
              </div>
            )}

            <button
              className="primary-btn full"
              disabled={busy}
            >
              {busy ? (
                "Authenticating…"
              ) : (
                <>
                  Continue securely
                  <ArrowRight size={17} />
                </>
              )}
            </button>
          </form>

          <div className="login-note">
            <span className="secure-icon">
              <ShieldCheck size={15} />
            </span>

            Your Firebase token is sent to the backend only
            over the configured API connection.
          </div>
        </section>
      </main>
    </div>
  );
}