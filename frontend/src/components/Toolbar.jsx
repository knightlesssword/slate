// Formatting controls wired to the TipTap editor instance.
export default function Toolbar({ editor }) {
  if (!editor) return null;

  const btn = (label, isActive, onClick, title) => (
    <button
      type="button"
      title={title}
      className={isActive ? "active" : ""}
      onClick={onClick}
    >
      {label}
    </button>
  );

  return (
    <div className="toolbar">
      {btn(
        <b>B</b>,
        editor.isActive("bold"),
        () => editor.chain().focus().toggleBold().run(),
        "Bold"
      )}
      {btn(
        <i>I</i>,
        editor.isActive("italic"),
        () => editor.chain().focus().toggleItalic().run(),
        "Italic"
      )}
      {btn(
        <u>U</u>,
        editor.isActive("underline"),
        () => editor.chain().focus().toggleUnderline().run(),
        "Underline"
      )}

      <span style={{ width: 8 }} />

      {btn(
        "H1",
        editor.isActive("heading", { level: 1 }),
        () => editor.chain().focus().toggleHeading({ level: 1 }).run(),
        "Heading 1"
      )}
      {btn(
        "H2",
        editor.isActive("heading", { level: 2 }),
        () => editor.chain().focus().toggleHeading({ level: 2 }).run(),
        "Heading 2"
      )}
      {btn(
        "P",
        editor.isActive("paragraph"),
        () => editor.chain().focus().setParagraph().run(),
        "Normal text"
      )}

      <span style={{ width: 8 }} />

      {btn(
        "• List",
        editor.isActive("bulletList"),
        () => editor.chain().focus().toggleBulletList().run(),
        "Bulleted list"
      )}
      {btn(
        "1. List",
        editor.isActive("orderedList"),
        () => editor.chain().focus().toggleOrderedList().run(),
        "Numbered list"
      )}
    </div>
  );
}
