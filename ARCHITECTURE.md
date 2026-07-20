# Architecture Note (Plan Stage)

> The *planned* architecture, written before implementation. It records what is being
> prioritized and why, and will be updated with any deviations at submission.

## High-level shape

```
Browser (React + Vite + TipTap)
        |
        |  HTTP / JSON  (access token in Authorization header; CORS enabled)
        v
FastAPI (REST)
  ├── /login     seeded users → access token (hashed-password verify)  ├── /documents CRUD + rename + upload-import
  └── /documents/{id}/share  share by email
        |
        v
SQLite (SQLAlchemy)  — users, documents, shares
```

The React SPA talks to a **FastAPI** service over REST. FastAPI was chosen to
demonstrate API design, validation, business logic, and persistence within the scope
of a full-stack assessment. CORS is configured from the start since the deployed
frontend and API live on different origins.

## Data model (planned)

**users**: id, email (unique), password_hash, display_name

**documents**: id, owner_id → users, title (non-empty), content_json (TipTap JSON), created_at, updated_at

**shares**: document_id → documents, user_id → users, unique(document_id, user_id)

## Access control (the important logic)

Enforced in the API layer:
- **Read / update a document** only if the caller is the **owner** OR appears in
  `shares` for that document. Anyone else → **403**.
- **Create** sets `owner_id` to the caller.
- **Manage shares / delete** only by the owner.
- **Sharing validation**: unknown user and duplicate share are rejected.

*Owned vs shared* is derived from whether `owner_id == current_user`.
This is exactly what the automated test covers (owner shares → grantee 200 → outsider 403).

## API surface (locked)

```
POST /login                    → { token }
GET  /me
GET  /users
GET  /documents                → owned + shared, flagged
POST /documents                → create
GET  /documents/{id}
PUT  /documents/{id}           → title / content
POST /documents/import         → upload .txt/.md → new document
POST /documents/{id}/share     → share by email (rejects unknown user + duplicate)
```

## Frontend structure (planned)

```
src/
  lib/api.js             # fetch wrapper, attaches JWT
  auth/                  # login, session context
  pages/
    Dashboard.jsx        # My documents / Shared with me
    Editor.jsx           # TipTap editor, title, manual save + saved state
  components/
    Toolbar.jsx          # bold/italic/underline/heading/list
    ShareDialog.jsx      # share by email
    UploadButton.jsx     # file input + validation
```

## Priorities & tradeoffs

1. **Correct, evaluable access control** — enforced server-side; the one meaningful test.
2. **Reliable persistence of formatting** — store structured TipTap JSON, not raw HTML.
3. **A usable, coherent editing flow** over matching Google Docs feature-for-feature.
4. **Manual save** over autosave — reliability over polish.
5. **Scoped file import** (`.txt`/`.md`) over broad, fragile format support.

## Known limitations (by design)

- Last-write-wins on concurrent edits; no real-time sync.
- No `.docx` import.
- Basic shared access (no per-user roles).
- Seeded auth rather than full account lifecycle.
- **SQLite persistence.** Chosen for scope and single-instance simplicity; not intended
  for horizontal scaling or high write concurrency. Swappable for managed Postgres via
  `DATABASE_URL` with no code changes.
- **Ephemeral public hosting.** On free-tier hosts with ephemeral filesystems, instances
  are not persistently maintained; a restart/redeploy/recycle can discard the disk and
  reset the SQLite database to an empty state, erasing runtime data. Mitigated with a
  persistent disk or an external database (see `README.md` → Known caveats).
