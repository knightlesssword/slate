import { useState } from "react";
import { ApiError, api } from "../lib/api";

// Owner-only dialog to share a document by email.
export default function ShareDialog({ doc, onClose, onShared }) {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const updated = await api.shareDocument(doc.id, email.trim());
      onShared(updated);
      setEmail("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to share");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="dialog-backdrop" onClick={onClose}>
      <div className="dialog" onClick={(e) => e.stopPropagation()}>
        <h2>Share "{doc.title}"</h2>
        <p className="muted">
          Enter the email of a registered user to grant access.
        </p>

        <form onSubmit={onSubmit}>
          <div className="dialog-row">
            <input
              className="full"
              type="email"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <button className="primary" type="submit" disabled={busy}>
              {busy ? "Sharing..." : "Share"}
            </button>
          </div>
        </form>

        {error && <p className="error">{error}</p>}

        <div>
          <p className="muted" style={{ marginBottom: 0 }}>
            Shared with:
          </p>
          {doc.shared_with?.length ? (
            <ul className="share-list">
              {doc.shared_with.map((u) => (
                <li key={u.id}>
                  {u.display_name} ({u.email})
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted">Not shared with anyone yet.</p>
          )}
        </div>

        <div className="dialog-actions">
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
