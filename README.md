# Slate

A lightweight collaborative document editor, inspired by Google Docs. Built as a
focused full-stack slice: create, edit (rich text), save, import files, and share
documents with other users.

- **Frontend:** React + Vite + TipTap
- **Backend:** FastAPI (REST)
- **Database:** SQLite (via SQLAlchemy)
- **Auth:** seeded users, login → access token (Argon2-hashed passwords)

See [`PLAN.md`](./PLAN.md) for scope and prioritization, and
[`ARCHITECTURE.md`](./ARCHITECTURE.md) for design decisions.

---

## What works

- Create, rename, edit, save, and reopen documents (formatting preserved).
- Rich text: bold, italic, underline, H1/H2/normal, bulleted & numbered lists.
- Import a `.txt` or `.md` file → a new editable document.
- Share a document with another user by email; dashboard separates
  **My documents** vs **Shared with me**.
- Access control enforced server-side (owner or granted user only; others get 403).
- Validation + error handling (empty title, unsupported/oversized file, unknown
  share target, duplicate share, unauthorized access, network errors).
- Automated tests for the sharing access rule.

## Supported file types

| Type   | Supported | Behavior                            |
| ------ | --------- | ----------------------------------- |
| `.txt` | Yes       | New document; lines → paragraphs.   |
| `.md`  | Yes       | New document; Markdown → TipTap doc. |
| `.docx`| No        | Out of scope (stated in UI).        |

Max upload size: ~1 MB.

---

## Prerequisites

- **Node.js** 20+ and npm
- **Python** 3.11+

## Run locally

Two processes: the API (port 8000) and the frontend (port 5173).

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt

# Create the SQLite DB and seed demo users:
python -m app.seed

# Run the API:
uvicorn app.main:app --reload --port 8000
```

API is now at `http://localhost:8000` (interactive docs at `/docs`).

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
# Point the app at the API (defaults to http://localhost:8000):
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

### Demo accounts

All use password `password123`:

- `alice@example.com`
- `bob@example.com`
- `carol@example.com`

Alice starts with a sample "Welcome to Slate" document. To demo sharing: log in as
Alice, open a document, click **Share**, enter `bob@example.com`, then log in as Bob
to see it under **Shared with me**. Carol will not see it (and gets a 403 if she tries
to open it directly).

---

## Tests

```bash
cd backend
.venv\Scripts\activate   # or source .venv/bin/activate
pytest
```

The test suite covers the sharing access rule end to end: owner creates → outsiders
get 403 → owner shares → grantee gets 200 → grantee can edit → unknown-user and
duplicate shares are rejected → non-owners cannot re-share.

---

## Deployment

- **Frontend** deploys as a static site (Vercel/Netlify). Set `VITE_API_URL` to the
  deployed API URL at build time.
- **Backend** deploys as a web service (Render/Fly/Railway). Set `CORS_ORIGINS` to the
  deployed frontend URL and `SECRET_KEY` to a strong random value. Run
  `python -m app.seed` once after first deploy to create demo users.

See `backend/render.yaml` for an example Render service definition.

## Known caveats

- **Persistence layer (SQLite).** The application uses SQLite as its datastore. This
  was a deliberate scope choice suited to a single-instance deployment, but it is not
  intended for horizontal scaling or high write concurrency. Migration to a managed
  Postgres instance is supported by setting `DATABASE_URL` and requires no application
  code changes.
- **Ephemeral public hosting.** Several free-tier hosting platforms provision
  containers with ephemeral filesystems. On such hosts, instances are not persistently
  maintained: on restart, redeploy, or idle-based recycling, the local disk — and
  therefore the SQLite database file — may be discarded and recreated from an empty
  state, resulting in loss of any documents and shares created at runtime. To retain
  data across restarts, either attach a persistent disk to the service (see
  `backend/render.yaml`, which mounts one) or point `DATABASE_URL` at an external
  managed database. Reviewers evaluating a free-tier deployment should be aware that
  runtime data may reset and can re-establish the demo state at any time by running
  `python -m app.seed`.
