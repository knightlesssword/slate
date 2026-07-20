# Slate — Project Plan

A lightweight collaborative document editor (Google Docs–inspired), built as a focused
full-stack slice within a 4–6 hour timebox.

> Guiding principle: **depth in a few areas over shallow coverage everywhere.**
> Ship create → edit → save → upload → share → reopen so it genuinely works end to end,
> with a real backend that can be evaluated as engineering — not as configuration.

---

## 1. Scope decisions (confirmed)

| Area | Decision | Why |
|------|----------|-----|
| Frontend | React + Vite (existing scaffold) | Already scaffolded; no rewrite cost. |
| Editor | TipTap (ProseMirror) | Clean bold/italic/underline/headings/lists; stores structured JSON. |
| Backend | **FastAPI (REST)** | Tangible backend to evaluate: routing, validation, auth, sharing endpoints, tests. |
| DB | **SQLite** via SQLAlchemy | Zero external DB to provision; trivial local run; fine for this scope. |
| Auth | **Seeded users**, login endpoint, password-hash verify, single access token | Auth is plumbing, not the product; keep it minimal but real. No registration/refresh/reset. |
| File handling | Backend endpoint parses upload into a document | Backend does the work → product-relevant and evaluable. |
| Save | **Manual save** (explicit button + saved/unsaved indicator) | Reliable; no debounce/race/dirty-state risk. |
| Deployment | Static frontend (Vercel/Netlify) + **FastAPI on Render/Fly free tier**; **CORS configured from the start** | A real backend needs a real host; free and reviewer-testable. |

### Why FastAPI
FastAPI was chosen to demonstrate API design, validation, business logic, and
persistence within the scope of a full-stack assessment.

### Assumptions
- "Collaborative" = **sharing + access control**, not real-time multi-cursor editing (stretch).
- Reviewers get 2 seeded accounts (`alice@example.com`, `bob@example.com`, known passwords) to demo owned vs shared.
- Supported upload types are **limited on purpose** (§3), stated in UI + README.
- One editor at a time per document; concurrent edits are last-write-wins (documented, not solved).

---

## 2. Core features (must ship)

Maps 1:1 to the assignment's required capabilities.

### 2.1 Document creation & editing
- Create a new document; **rename** (inline title); edit rich text in the browser (TipTap):
  **Bold**, *Italic*, <u>Underline</u>, Headings (H1/H2), bulleted & numbered lists.
- **Manual Save** persists content (TipTap JSON); reopen preserves formatting.
- Clear **saved / unsaved** indicator.

### 2.2 File upload (scoped)
- Upload a **`.txt` or `.md`** file → backend parses it into a **new editable document** (Markdown → TipTap document).
- `.docx` is **out of scope** (stated in UI + README) — reliable Word parsing is a time sink;
  `.md`/`.txt` demonstrates the same "import a file into an editable doc" capability.
- Type + size validated on client and server; clear error messages.

### 2.3 Sharing
- Each document has one **owner** (creator).
- Owner shares by **email** with another registered user, granting access.
- Dashboard separates **"My documents"** vs **"Shared with me."**
- Access control enforced by the API: only the owner or a granted user may read/edit a document;
  everyone else gets **403**. (Basic access by design — no per-user roles; that's a stretch.)

### 2.4 Persistence
- Documents (title, content, owner, timestamps) and shares stored in SQLite.
- Survive refresh; formatting preserved via stored TipTap JSON.

### 2.5 Engineering quality
- README with local setup + run instructions and env vars.
- Live deployed URL (frontend + API).
- Client + server validation and visible error handling (empty title, bad file, unauthorized, network failure).
- **At least one meaningful automated test** — targets the **sharing access rule** (§5), the important feature.
- `ARCHITECTURE.md`, `AI_NOTES.md`, `SUBMISSION.md`.

---

## 3. Supported file types (stated clearly)

| Type | Supported | Behavior |
|------|-----------|----------|
| `.txt` | ✅ | New document; lines → paragraphs. |
| `.md`  | ✅ | New document; Markdown → TipTap document. |
| `.docx`| ❌ | Not supported (out of scope) — shown as a notice in UI. |
| Others | ❌ | Rejected with a clear message. |

Max file size: **~1 MB** (validated).

---

## 4. Deliberate cuts (deprioritized, and why)

| Cut | Reason |
|-----|--------|
| Real-time collaborative editing (multi-cursor, CRDT/OT) | High complexity; not required. Sharing + access control satisfies the "collaborative" intent. |
| `.docx` import | Reliable Word parsing is a rabbit hole; `.md`/`.txt` proves the capability. |
| Fine-grained roles (viewer / editor / commenter) | Basic shared access is the requirement; roles are a stretch. |
| Autosave | Manual save is reliable and loses no points; autosave adds debounce/race/dirty-state risk. |
| Registration / refresh tokens / verification / reset | Auth is plumbing; seeded users + login is enough to demo sharing. |
| Comments / suggestions / version history | Optional stretch; not core. |
| Folders, search, trash | Out of scope for a focused slice. |

---

## 5. Success criteria (treat as tests to pass)

On the **deployed URL**, a reviewer can:

1. Log in as **Alice** (seeded).
2. Create a document, type formatted text (bold/heading/list), **Save**, and see it persist after refresh.
3. **Rename** the document.
4. **Upload** a `.md` file → new editable document with formatting intact.
5. **Share** the document with **Bob** by email.
6. Log in as **Bob**, see the doc under **"Shared with me,"** open and edit it.
7. Confirm a third user **cannot** access a document never shared with them → **403**.
8. Confirm sharing validation: sharing with a **non-existent user** and a **duplicate share** are both rejected.
9. See graceful handling of: invalid file type, empty title, unauthorized access, network error.
10. `pytest` passes the sharing-access test.

If anything is incomplete at the time limit, `SUBMISSION.md` states it explicitly
(working / incomplete / next 2–4h).

---

## 6. Time budget (of 4–6h)

| Task | Est. (min) |
|------|-----------|
| Backend: FastAPI app, models, DB, seed | 60 |
| Auth: seeded users + login + hash verify + token | 45 |
| Editor: TipTap + save/load/rename | 75 |
| Upload: parse `.txt`/`.md` → document | 30 |
| Sharing: endpoints + UI (owned vs shared) | 45 |
| Deploy: frontend + API host | 45 |
| Docs (README/ARCH/AI/SUBMISSION) | 45 |
| Testing (sharing access rule) | 30 |

**Prioritization rule:** if time slips, **drop features, not quality.** Cuts in §4 protect the core.

---

## 7. Possible stretch (only if core is solid)

- Export to Markdown / PDF.
- Document version history (snapshot on save).
- "Last edited by / at" indicator.
- Viewer vs editor role on shares.

None pursued at the expense of §2.

---

## 8. Locked data model

```
User
----
id
email          (unique)
password_hash
display_name

Document
--------
id
owner_id       → User
title
content_json   (TipTap JSON)
created_at
updated_at

Share
-----
document_id    → Document
user_id        → User
                (unique together: document_id + user_id)
```

## 9. Locked API surface

Frozen before coding; if these don't change, the rest gets much easier.

```
POST   /login                      → { token }
GET    /me

GET    /users                      → for share picker / validation

GET    /documents                  → owned + shared (flagged)
POST   /documents                  → create
GET    /documents/{id}
PUT    /documents/{id}             → title / content
POST   /documents/import           → upload .txt/.md → new document

POST   /documents/{id}/share       → share by email (rejects unknown user + duplicate)
```
