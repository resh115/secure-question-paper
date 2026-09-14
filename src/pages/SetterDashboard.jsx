import React, { useMemo, useState } from "react";

import {
  UploadCloud,
  FileText,
  CalendarDays,
  Clock3,
  LockKeyhole,
  ShieldCheck,
  CheckCircle2,
  X,
  LoaderCircle,
  Copy,
  Check,
} from "lucide-react";

import { apiFetch } from "../lib/api";

export default function SetterDashboard({ user }) {
  const [file, setFile] = useState(null);
  const [examName, setExamName] = useState("");

  // Separate date and time
  const [releaseDate, setReleaseDate] = useState("");
  const [releaseTime, setReleaseTime] = useState("");

  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const fileLabel = useMemo(
    () =>
      file
        ? `${file.name} • ${(file.size / 1024 / 1024).toFixed(2)} MB`
        : "PDF up to 10 MB",
    [file]
  );

  function chooseFile(event) {
    const next = event.target.files?.[0];

    setError("");
    setResult(null);
    setCopied(false);

    if (!next) {
      setFile(null);
      return;
    }

    if (next.type !== "application/pdf") {
      setFile(null);
      setError("Please select a PDF question paper.");
      return;
    }

    if (next.size > 10 * 1024 * 1024) {
      setFile(null);
      setError("The backend accepts files up to 10 MB.");
      return;
    }

    setFile(next);
  }

  async function copyPaperId() {
    if (!result?.paper_id) {
      return;
    }

    try {
      await navigator.clipboard.writeText(result.paper_id);

      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 1800);
    } catch {
      setError("Unable to copy the Paper ID.");
    }
  }

  async function securePaper(event) {
    event.preventDefault();

    setError("");
    setResult(null);
    setCopied(false);

    if (!file) {
      setError("Select a PDF question paper.");
      return;
    }

    if (!examName.trim()) {
      setError("Enter the examination name.");
      return;
    }

    if (!releaseDate) {
      setError("Select the release date.");
      return;
    }

    if (!releaseTime) {
      setError("Select the release time.");
      return;
    }

    /*
      Combine the selected date and time.

      Example:
      releaseDate = 2026-09-15
      releaseTime = 14:30

      Result:
      2026-09-15T14:30

      The backend interprets this as IST.
    */
    const releaseAt = `${releaseDate}T${releaseTime}`;

    const selectedTime = new Date(releaseAt);
    const currentTime = new Date();

    if (Number.isNaN(selectedTime.getTime())) {
      setError("Invalid release date or time.");
      return;
    }

    if (selectedTime <= currentTime) {
      setError("Release time must be in the future.");
      return;
    }

    try {
      setBusy(true);

      const form = new FormData();

      form.append("file", file);
      form.append("exam_name", examName.trim());

      /*
        IMPORTANT:
        Do not convert this to UTC.

        The backend receives:
        YYYY-MM-DDTHH:mm

        and interprets it as IST.
      */
      form.append("release_at", releaseAt);

      const response = await apiFetch(
        "/api/question-papers/upload",
        {
          method: "POST",
          body: form,
        },
        user
      );

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          data.error ||
            data.details ||
            "Failed to secure question paper."
        );
      }

      setResult(data);

      setFile(null);
      setExamName("");
      setReleaseDate("");
      setReleaseTime("");

      const fileInput = document.getElementById(
        "question-paper-file"
      );

      if (fileInput) {
        fileInput.value = "";
      }
    } catch (err) {
      setError(
        err.message ||
          "Something went wrong while securing the paper."
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      {/* =========================================
          PAGE HEADER
          ========================================= */}

      <div className="page-heading">
        <div>
          <div className="eyebrow">
            <ShieldCheck size={15} />
            SETTER CONTROL
          </div>

          <h1>Secure a question paper</h1>

          <p>
            Upload once. Encrypt before storage.
            Distribute the recovery key as five
            threshold shares.
          </p>
        </div>

        <div className="heading-badge">
          <LockKeyhole size={17} />
          AES-256-GCM
          <span>+</span>
          3-of-5
        </div>
      </div>

      {/* =========================================
          MAIN GRID
          ========================================= */}

      <div className="dashboard-grid">
        {/* =======================================
            UPLOAD FORM
            ======================================= */}

        <section className="glass-card form-card">
          <div className="section-title">
            <div>
              <h2>New secure release</h2>

              <p>
                Exam metadata is stored with the
                encrypted artifact.
              </p>
            </div>

          </div>

          <form onSubmit={securePaper}>
            {/* ===================================
                EXAMINATION NAME
                =================================== */}

            <label htmlFor="exam-name">
              Examination name
            </label>

            <div className="input-wrap">
              <FileText size={18} />

              <input
                id="exam-name"
                type="text"
                value={examName}
                onChange={(e) =>
                  setExamName(e.target.value)
                }
                placeholder="e.g. Computer Networks — Semester Exam"
                disabled={busy}
                required
              />
            </div>

            {/* ===================================
                RELEASE DATE
                =================================== */}

            <label htmlFor="release-date">
              Release date
            </label>

            <div className="input-wrap date-picker-wrap">
              <CalendarDays size={18} />

              <input
                id="release-date"
                type="date"
                value={releaseDate}
                min={new Date()
                  .toISOString()
                  .split("T")[0]}
                onChange={(e) => {
                  setReleaseDate(e.target.value);
                  setError("");
                }}
                disabled={busy}
                required
              />
            </div>

            {/* ===================================
                RELEASE TIME
                =================================== */}

            <label htmlFor="release-time">
              Release time
            </label>

            <div className="input-wrap time-picker-wrap">
              <Clock3 size={18} />

              <input
                id="release-time"
                type="time"
                value={releaseTime}
                onChange={(e) => {
                  setReleaseTime(e.target.value);
                  setError("");
                }}
                disabled={busy}
                required
              />
            </div>

            <div className="time-note">
              <Clock3 size={13} />

              <span>
                Selected date and time are interpreted
                as Indian Standard Time (IST).
              </span>
            </div>

            {/* ===================================
                PDF UPLOAD
                =================================== */}

            <label>Question paper</label>

            <label
              htmlFor="question-paper-file"
              className={`dropzone ${
                file ? "has-file" : ""
              }`}
            >
              <input
                id="question-paper-file"
                type="file"
                accept="application/pdf,.pdf"
                onChange={chooseFile}
                disabled={busy}
                hidden
              />

              {file ? (
                <>
                  <CheckCircle2 size={28} />

                  <strong>{file.name}</strong>

                  <span>{fileLabel}</span>

                  <small>
                    Click to replace
                  </small>
                </>
              ) : (
                <>
                  <UploadCloud size={30} />

                  <strong>
                    Drop your PDF here
                  </strong>

                  <span>
                    or click to browse
                  </span>

                  <small>
                    {fileLabel}
                  </small>
                </>
              )}
            </label>

            {/* ===================================
                ERROR
                =================================== */}

            {error && (
              <div className="error-box">
                {error}
              </div>
            )}

            {/* ===================================
                SUCCESS
                =================================== */}

            {result && (
              <div className="success-box secure-success">
                <div className="success-icon">
                  <CheckCircle2 size={19} />
                </div>

                <div className="success-content">
                  <strong>
                    Question paper secured
                  </strong>

                  {/* PAPER ID */}

                  <div className="paper-id-row">
                    <span className="success-label">
                      Paper ID
                    </span>

                    <code className="paper-id">
                      {result.paper_id}
                    </code>

                    <button
                      type="button"
                      className="copy-paper-btn"
                      onClick={copyPaperId}
                      title="Copy Paper ID"
                    >
                      {copied ? (
                        <>
                          <Check size={14} />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy size={14} />
                          Copy
                        </>
                      )}
                    </button>
                  </div>

                  {/* RELEASE */}

                  {result.release_at && (
                    <div className="release-info">
                      <span className="success-label">
                        Release
                      </span>

                      <span className="release-value">
                        {result.release_at}
                      </span>
                    </div>
                  )}
                </div>

                <button
                  type="button"
                  className="success-close"
                  onClick={() => {
                    setResult(null);
                    setCopied(false);
                  }}
                  aria-label="Close"
                >
                  <X size={15} />
                </button>
              </div>
            )}

            {/* ===================================
                SECURE BUTTON
                =================================== */}

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

                  Securing in cloud…
                </>
              ) : (
                <>
                  <LockKeyhole size={17} />

                  Encrypt & secure paper
                </>
              )}
            </button>
          </form>
        </section>

        {/* =======================================
            SECURITY PIPELINE
            ======================================= */}

        <aside className="side-stack">
          <section className="glass-card process-card">
            <div className="section-title">
              <div>
                <h2>Protection pipeline</h2>

                <p>
                  What happens after you click secure.
                </p>
              </div>
            </div>

            <div className="process-row">
              <span>01</span>

              <div>
                <strong>
                  AES-256-GCM
                </strong>

                <small>
                  Paper encrypted in memory
                </small>
              </div>

              <CheckCircle2 size={16} />
            </div>

            <div className="process-row">
              <span>02</span>

              <div>
                <strong>
                  Shamir 3-of-5
                </strong>

                <small>
                  AES key split into five shares
                </small>
              </div>

              <CheckCircle2 size={16} />
            </div>

            <div className="process-row">
              <span>03</span>

              <div>
                <strong>
                  Cloud distribution
                </strong>

                <small>
                  Encrypted paper + shares stored
                </small>
              </div>

              <CheckCircle2 size={16} />
            </div>

            <div className="process-row">
              <span>04</span>

              <div>
                <strong>
                  Audit event
                </strong>

                <small>
                  Security action recorded
                </small>
              </div>

              <CheckCircle2 size={16} />
            </div>
          </section>

          {/* =====================================
              SECURITY NOTICE
              ===================================== */}

          <section className="glass-card notice-card">
            <ShieldCheck size={21} />

            <div>
              <strong>
                Paper stays locked
              </strong>

              <p>
                Storage never contains the plaintext
                question paper. Authorized release is
                handled by the backend.
              </p>
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}