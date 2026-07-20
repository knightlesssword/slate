import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import Toolbar from "../components/Toolbar";
import ShareDialog from "../components/ShareDialog";
import { ApiError, api } from "../lib/api";

const EMPTY_DOC = { type: "doc", content: [{ type: "paragraph" }] };

function parseContent(content_json) {
  if (!content_json) return EMPTY_DOC;
  try {
    return JSON.parse(content_json);
  } catch {
    return EMPTY_DOC;
  }
}

export default function Editor() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [doc, setDoc] = useState(null);
  const [title, setTitle] = useState("");
  const [dirty, setDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [saveError, setSaveError] = useState("");
  const [showShare, setShowShare] = useState(false);

  const editor = useEditor({
    extensions: [StarterKit, Underline],
    content: EMPTY_DOC,
    onUpdate: () => setDirty(true),
  });

  // Load document once the editor instance exists.
  useEffect(() => {
    if (!editor) return;
    let active = true;
    (async () => {
      try {
        const data = await api.getDocument(id);
        if (!active) return;
        setDoc(data);
        setTitle(data.title);
        editor.commands.setContent(parseContent(data.content_json));
        setDirty(false);
      } catch (err) {
        if (!active) return;
        setLoadError(
          err instanceof ApiError ? err.message : "Failed to load document"
        );
      }
    })();
    return () => {
      active = false;
    };
  }, [editor, id]);

  async function onSave() {
    if (!editor || !doc) return;
    const trimmed = title.trim();
    if (!trimmed) {
      setSaveError("Title must not be empty.");
      return;
    }
    setSaving(true);
    setSaveError("");
    try {
      const patch = {
        title: trimmed,
        content_json: JSON.stringify(editor.getJSON()),
      };
      const updated = await api.updateDocument(doc.id, patch);
      setDoc((prev) => ({ ...prev, ...updated }));
      setTitle(updated.title);
      setDirty(false);
    } catch (err) {
      setSaveError(err instanceof ApiError ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  }

  // Ctrl/Cmd+S saves.
  useEffect(() => {
    function onKey(e) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        onSave();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  if (loadError) {
    return (
      <div className="center-note">
        <p className="error">{loadError}</p>
        <button onClick={() => navigate("/")}>Back to documents</button>
      </div>
    );
  }

  const saveLabel = saving
    ? "Saving..."
    : dirty
      ? "Unsaved changes"
      : "All changes saved";

  return (
    <div className="editor-page">
      <div className="editor-bar">
        <button onClick={() => navigate("/")}>← Docs</button>
        <input
          className="title-input"
          value={title}
          onChange={(e) => {
            setTitle(e.target.value);
            setDirty(true);
          }}
          placeholder="Untitled document"
          aria-label="Document title"
        />
        <span className={`save-state ${dirty ? "dirty" : ""}`}>
          {saveLabel}
        </span>
        {doc?.is_owner && (
          <button onClick={() => setShowShare(true)}>Share</button>
        )}
        <button className="primary" onClick={onSave} disabled={saving}>
          Save
        </button>
      </div>

      <Toolbar editor={editor} />

      {saveError && (
        <p className="error" style={{ padding: "0 1.5rem" }}>
          {saveError}
        </p>
      )}
      {doc && !doc.is_owner && (
        <p className="muted" style={{ padding: "0.4rem 1.5rem 0" }}>
          Shared with you by {doc.owner_email}. You can edit and save.
        </p>
      )}

      <div className="editor-scroll">
        <div className="editor-sheet">
          <EditorContent editor={editor} />
        </div>
      </div>

      {showShare && doc && (
        <ShareDialog
          doc={doc}
          onClose={() => setShowShare(false)}
          onShared={(updated) =>
            setDoc((prev) => ({ ...prev, ...updated }))
          }
        />
      )}
    </div>
  );
}
