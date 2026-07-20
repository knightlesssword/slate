import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import { ApiError, api } from "../lib/api";

const ACCEPTED = ".txt,.md";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const fileRef = useRef(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const data = await api.listDocuments();
        if (active) setDocs(data);
      } catch (err) {
        if (active)
          setError(err instanceof ApiError ? err.message : "Failed to load");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  async function onCreate() {
    setBusy(true);
    setError("");
    try {
      const doc = await api.createDocument("Untitled document");
      navigate(`/documents/${doc.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create");
      setBusy(false);
    }
  }

  async function onUpload(e) {
    const file = e.target.files?.[0];
    e.target.value = ""; // allow re-selecting the same file
    if (!file) return;

    const lower = file.name.toLowerCase();
    if (!lower.endsWith(".txt") && !lower.endsWith(".md")) {
      setError("Only .txt and .md files are supported.");
      return;
    }

    setBusy(true);
    setError("");
    try {
      const doc = await api.importDocument(file);
      navigate(`/documents/${doc.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed");
      setBusy(false);
    }
  }

  const owned = docs.filter((d) => d.is_owner);
  const shared = docs.filter((d) => !d.is_owner);

  return (
    <>
      <div className="topbar">
        <span className="brand">Slate</span>
        <div className="dash-actions">
          <span className="muted">{user?.display_name}</span>
          <button onClick={logout}>Sign out</button>
        </div>
      </div>

      <div className="container">
        <div className="dash-head">
          <h2 style={{ margin: 0 }}>Documents</h2>
          <div className="dash-actions">
            <button
              onClick={() => fileRef.current?.click()}
              disabled={busy}
              title="Import a .txt or .md file"
            >
              Upload file
            </button>
            <button className="primary" onClick={onCreate} disabled={busy}>
              New document
            </button>
            <input
              ref={fileRef}
              type="file"
              accept={ACCEPTED}
              onChange={onUpload}
              style={{ display: "none" }}
            />
          </div>
        </div>

        <p className="muted">Supported upload types: .txt and .md (max ~1 MB).</p>

        {error && <p className="error">{error}</p>}
        {loading && <p className="muted">Loading...</p>}

        {!loading && (
          <>
            <h3 className="section-title">My documents</h3>
            {owned.length === 0 ? (
              <p className="muted">
                No documents yet. Create one or upload a file.
              </p>
            ) : (
              <div className="doc-list">
                {owned.map((d) => (
                  <DocRow key={d.id} doc={d} />
                ))}
              </div>
            )}

            <h3 className="section-title">Shared with me</h3>
            {shared.length === 0 ? (
              <p className="muted">Nothing has been shared with you yet.</p>
            ) : (
              <div className="doc-list">
                {shared.map((d) => (
                  <DocRow key={d.id} doc={d} showOwner />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </>
  );
}

function DocRow({ doc, showOwner }) {
  return (
    <Link className="doc-row" to={`/documents/${doc.id}`}>
      <span className="doc-title">{doc.title}</span>
      <span className="muted">
        {showOwner ? (
          <>Shared by {doc.owner_email}</>
        ) : (
          <span className="badge">Owner</span>
        )}
      </span>
    </Link>
  );
}
