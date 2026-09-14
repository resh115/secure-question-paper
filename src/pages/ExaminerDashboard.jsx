import React, { useState } from "react";
import {
  KeyRound,
  Search,
  ShieldCheck,
  LockKeyhole,
  FileText,
  Clock3,
  Eye,
  LoaderCircle,
  AlertTriangle,
} from "lucide-react";

import { apiFetch } from "../lib/api";

export default function ExaminerDashboard({ user }) {
  const [paperId, setPaperId] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [paperUrl, setPaperUrl] = useState("");

  async function releasePaper(event) {
    event.preventDefault();

    const trimmedPaperId = paperId.trim();

    if (!trimmedPaperId) {
      setError("Enter the paper ID supplied by the setter.");
      return;
    }

    setBusy(true);
    setError("");

    // Remove previously displayed PDF
    if (paperUrl) {
      URL.revokeObjectURL(paperUrl);
      setPaperUrl("");
    }

    try {
      /*
       * Send the secure paper ID to Flask.
       *
       * apiFetch automatically adds:
       * Authorization: Bearer <Firebase ID token>
       */
      const response = await apiFetch(
        `/api/release/${encodeURIComponent(trimmedPaperId)}`,
        {
          method: "POST",
        }
      );

      /*
       * IMPORTANT:
       * Flask can return JSON errors such as:
       *
       * 404 Question paper not found
       * 403 Question paper is still locked
       * 500 Question paper decryption failed
       *
       * Never treat those responses as PDF files.
       */
      if (!response.ok) {
        let data = {};

        try {
          data = await response.json();
        } catch {
          // Response was not JSON.
        }

        throw new Error(
          data.error ||
            `Release failed with HTTP ${response.status}.`
        );
      }

      /*
       * Successful release must return a PDF.
       */
      const contentType =
        response.headers.get("content-type") || "";

      if (!contentType.includes("application/pdf")) {
        throw new Error(
          "Release succeeded, but the server did not return a PDF."
        );
      }

      /*
       * Receive the decrypted PDF.
       *
       * The backend decrypts it in memory and sends
       * the PDF bytes directly to the browser.
       */
      const blob = await response.blob();

      if (!blob.size) {
        throw new Error(
          "The server returned an empty question paper."
        );
      }

      const url = URL.createObjectURL(blob);

      setPaperUrl(url);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to release question paper."
      );

      setPaperUrl("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      {/* --------------------------------------------- */}
      {/* PAGE HEADER */}
      {/* --------------------------------------------- */}

      <div className="page-heading">
        <div>
          <div className="eyebrow">
            <Eye size={15} />
            EXAMINER CONTROL
          </div>

          <h1>Controlled paper release</h1>

          <p>
            The question paper is reconstructed and decrypted
            only after the release controller permits access.
          </p>
        </div>

        <div className="heading-badge">
          <Clock3 size={17} />
          TIME-LOCKED
        </div>
      </div>

      {/* --------------------------------------------- */}
      {/* MAIN EXAMINER GRID */}
      {/* --------------------------------------------- */}

      <div className="examiner-grid">
        {/* ------------------------------------------- */}
        {/* RELEASE CONTROL CARD */}
        {/* ------------------------------------------- */}

        <section className="glass-card release-card">
          <div className="release-icon">
            <KeyRound size={27} />
          </div>

          <h2>Unlock examination paper</h2>

          <p className="muted">
            Enter the secure paper ID. The backend verifies
            your Firebase identity and examiner role before
            attempting release.
          </p>

          <form onSubmit={releasePaper}>
            <label htmlFor="paper-id">
              Secure paper ID
            </label>

            <div className="input-wrap">
              <Search size={18} />

              <input
                id="paper-id"
                type="text"
                value={paperId}
                onChange={(event) => {
                  setPaperId(event.target.value);
                  setError("");
                }}
                placeholder="e.g. 3a7f…"
                autoComplete="off"
                spellCheck="false"
                disabled={busy}
              />
            </div>

            {/* --------------------------------------- */}
            {/* ERROR */}
            {/* --------------------------------------- */}

            {error && (
              <div className="error-box">
                <AlertTriangle size={17} />
                <span>{error}</span>
              </div>
            )}

            {/* --------------------------------------- */}
            {/* RELEASE BUTTON */}
            {/* --------------------------------------- */}

            <button
              type="submit"
              className="primary-btn full"
              disabled={busy}
            >
              {busy ? (
                <>
                  <LoaderCircle
                    className="spin"
                    size={17}
                  />
                  Verifying release…
                </>
              ) : (
                <>
                  <LockKeyhole size={17} />
                  Release securely
                </>
              )}
            </button>
          </form>

          {/* --------------------------------------- */}
          {/* SECURITY CHECKS */}
          {/* --------------------------------------- */}

          <div className="release-checks">
            <span>
              <ShieldCheck size={15} />
              Firebase identity
            </span>

            <span>
              <ShieldCheck size={15} />
              Examiner RBAC
            </span>

            <span>
              <ShieldCheck size={15} />
              Time control
            </span>

            <span>
              <ShieldCheck size={15} />
              Audit logging
            </span>
          </div>
        </section>

        {/* ------------------------------------------- */}
        {/* SECURE PDF VIEWER */}
        {/* ------------------------------------------- */}

        <section className="glass-card viewer-card">
          <div className="viewer-header">
            <div>
              <div className="card-kicker">
                SECURE VIEWER
              </div>

              <h2>Question paper</h2>
            </div>

            {paperUrl && (
              <span className="live-label">
                RELEASED
              </span>
            )}
          </div>

          {/* ----------------------------------------- */}
          {/* PDF AVAILABLE */}
          {/* ----------------------------------------- */}

          {paperUrl ? (
            <iframe
              title="Decrypted question paper"
              src={paperUrl}
              className="pdf-viewer"
            />
          ) : (
            /* --------------------------------------- */
            /* EMPTY VIEWER */
            /* --------------------------------------- */

            <div className="empty-viewer">
              <FileText size={38} />

              <strong>
                Paper not released
              </strong>

              <span>
                After successful release, the decrypted
                PDF will appear here in memory.
              </span>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}