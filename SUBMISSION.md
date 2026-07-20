# Submission — Slate

A lightweight collaborative document editor (Google Docs–inspired).

## Contents of this repository

| Item | Path |
| ---- | ---- |
| Frontend (React + Vite + TipTap) | `frontend/` |
| Backend (FastAPI + SQLite) | `backend/` |
| Local setup & run instructions | `README.md` |
| Project plan & scope decisions | `PLAN.md` |
| Architecture note | `ARCHITECTURE.md` |
| AI workflow note | `AI_NOTES.md` |
| This file | `SUBMISSION.md` |
| Automated test (sharing access rule) | `backend/tests/test_sharing.py` |
| Example deploy config | `backend/render.yaml`, `frontend/vercel.json` |

## Credentials / seeded accounts

All passwords are `password123`:

- `alice@example.com` (owns a sample document)
- `bob@example.com`
- `carol@example.com`

Sharing demo: log in as Alice → open a doc → **Share** with `bob@example.com` →
log in as Bob → see it under **Shared with me**. Carol cannot see or open it.

## What is working

- Create, rename, edit, save, and reopen documents with formatting preserved.
- Rich text: bold, italic, underline, H1/H2/normal text, bulleted & numbered lists.
- Import `.txt` / `.md` files into new editable documents.
- Share by email; owned vs shared clearly separated on the dashboard.
- Server-side access control (owner or grantee only; others receive 403).
- Validation & error handling (empty title, bad/oversized file, unknown or duplicate
  share target, unauthorized access, network failure).
- Automated tests pass (`cd backend && pytest`).
- Frontend builds and lints clean.

## What is intentionally out of scope

- Real-time collaborative editing (multi-cursor). Sharing + access control covers the
  collaborative intent within the timebox.
- `.docx` import (only `.txt` / `.md`).
- Fine-grained roles (viewer vs editor). Shared users can view and edit.
- Full account lifecycle (registration, password reset, email verification) — seeded
  users instead.
- Autosave — manual save with a saved/unsaved indicator.

## Known limitations

- Concurrent edits are last-write-wins (no real-time sync).
- **SQLite datastore.** SQLite is used as the persistence layer — a deliberate scope
  choice for a single-instance deployment, not intended for horizontal scaling or high
  write concurrency. It can be swapped for managed Postgres via `DATABASE_URL` with no
  code changes.
- **Ephemeral public hosting.** On free-tier hosts with ephemeral filesystems,
  instances are not persistently maintained: a restart, redeploy, or idle recycling can
  discard the local disk and recreate the SQLite database from an empty state, erasing
  documents and shares created at runtime. Mitigate by attaching a persistent disk (see
  `backend/render.yaml`) or using an external database; the demo state can be restored
  at any time with `python -m app.seed`. Details in `README.md` → Known caveats.

## What I would build next with another 2–4 hours

1. Viewer vs editor roles on shares.
2. Export to Markdown / PDF.
3. Document version history (snapshot on save).
4. "Last edited by / at" indicator.

## Links (fill in before final submission)

- Github URL: `https://github.com/knightlesssword/slate`
- Live product URL: `https://slate-tau-henna.vercel.app/`
- API URL: `https://slate-rxet.onrender.com`
