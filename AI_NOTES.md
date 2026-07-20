# AI Workflow Note

## Tools used

- **Kilo (agentic coding assistant, this session)** — used for planning, scaffolding
  the backend and frontend, writing the test, and iterating on lint/build errors.

## Where AI materially sped things up

- **Boilerplate and wiring.** SQLAlchemy models, Pydantic schemas, the FastAPI routers,
  and the React API client / auth context are repetitive plumbing. Generating these
  from a locked data model and API surface saved the most time.
- **Markdown → TipTap conversion.** Mapping `markdown-it` tokens to TipTap's document
  JSON shape is fiddly; drafting it with AI and then verifying the JSON output against a
  real `.md` file was faster than writing it cold.
- **CSS.** A clean, minimal stylesheet was generated in one pass rather than
  hand-tuned.

## What was changed or rejected

- **Rejected Supabase.** An earlier plan used Supabase for auth/DB/storage. It was
  rejected because it leaves almost no backend to evaluate for a full-stack role; the
  project was pivoted to FastAPI + SQLite so there is real API/validation/business-logic
  code.
- **Rejected autosave.** Considered debounced autosave; cut it in favor of manual save
  to avoid race/dirty-state bugs within the timebox.
- **Fixed AI defaults.** `EmailStr` combined with seeded `@demo.test` addresses failed
  validation (`.test` is reserved); switched demo accounts to `@example.com`.
- **Fixed a deprecated pattern.** The generated FastAPI startup used the deprecated
  `@app.on_event`; replaced with a `lifespan` handler.
- **Tightened lint issues.** Split the `useAuth` hook into its own module and reworked a
  data-loading effect to satisfy the React lint rules rather than disabling them.

## How correctness was verified

- **Automated tests** (`pytest`) for the sharing access rule — the most important logic.
- **Live API smoke tests** against a running server: created a document, confirmed
  outsiders get 403, shared with a second user, confirmed the grantee gets 200 and a
  third user still gets 403, imported a real `.md` file and inspected the resulting
  TipTap JSON, and confirmed unsupported file types return 400.
- **Build + lint** on the frontend (`npm run build`, `npm run lint`) both clean.
- **Manual UX check** via the running dev server.

AI accelerated the mechanical work; the scope decisions, the access-control design, and
the verification were driven and checked by hand.
