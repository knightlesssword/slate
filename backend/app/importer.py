"""Convert uploaded .txt / .md content into a TipTap document (JSON string).

This is deliberately small: it covers the common Markdown constructs the editor
supports (headings, bold, italic, bullet/ordered lists, paragraphs). Anything it
does not recognise falls back to plain paragraphs, so import never fails on
unexpected input.
"""
import json

from markdown_it import MarkdownIt

SUPPORTED_EXTENSIONS = (".txt", ".md")

_md = MarkdownIt("commonmark")


def _text_node(text: str) -> dict:
    return {"type": "text", "text": text}


def _inline_to_nodes(inline_tokens) -> list[dict]:
    """Flatten inline markdown tokens into TipTap text nodes with marks."""
    nodes: list[dict] = []
    active_marks: list[dict] = []

    for tok in inline_tokens:
        if tok.type == "text" and tok.content:
            node = _text_node(tok.content)
            if active_marks:
                node["marks"] = [dict(m) for m in active_marks]
            nodes.append(node)
        elif tok.type == "code_inline" and tok.content:
            nodes.append({"type": "text", "text": tok.content,
                          "marks": [{"type": "code"}]})
        elif tok.type in ("strong_open", "em_open"):
            active_marks.append(
                {"type": "bold" if tok.type == "strong_open" else "italic"}
            )
        elif tok.type in ("strong_close", "em_close"):
            if active_marks:
                active_marks.pop()
        elif tok.type == "softbreak" or tok.type == "hardbreak":
            nodes.append({"type": "hardBreak"})

    return nodes


def _paragraph(text: str) -> dict:
    content = [_text_node(text)] if text else []
    return {"type": "paragraph", "content": content}


def _plain_text_doc(raw: str) -> dict:
    """Fallback used for .txt: each line becomes a paragraph."""
    lines = raw.replace("\r\n", "\n").split("\n")
    paragraphs = [_paragraph(line) for line in lines] or [_paragraph("")]
    return {"type": "doc", "content": paragraphs}


def markdown_to_tiptap(raw: str) -> dict:
    tokens = _md.parse(raw)
    content: list[dict] = []
    list_stack: list[dict] = []

    i = 0
    while i < len(tokens):
        tok = tokens[i]

        if tok.type == "heading_open":
            level = int(tok.tag[1])  # h1 -> 1
            inline = tokens[i + 1]
            content_target = (
                list_stack[-1]["content"] if list_stack else content
            )
            content_target.append({
                "type": "heading",
                "attrs": {"level": min(level, 3)},
                "content": _inline_to_nodes(inline.children or []),
            })
            i += 3  # heading_open, inline, heading_close
            continue

        if tok.type == "paragraph_open":
            inline = tokens[i + 1]
            para = {
                "type": "paragraph",
                "content": _inline_to_nodes(inline.children or []),
            }
            if list_stack:
                list_stack[-1]["content"].append(
                    {"type": "listItem", "content": [para]}
                )
            else:
                content.append(para)
            i += 3
            continue

        if tok.type in ("bullet_list_open", "ordered_list_open"):
            node = {
                "type": (
                    "bulletList"
                    if tok.type == "bullet_list_open"
                    else "orderedList"
                ),
                "content": [],
            }
            list_stack.append(node)
            i += 1
            continue

        if tok.type in ("bullet_list_close", "ordered_list_close"):
            node = list_stack.pop()
            target = list_stack[-1]["content"] if list_stack else content
            target.append(node)
            i += 1
            continue

        i += 1

    if not content:
        return _plain_text_doc(raw)
    return {"type": "doc", "content": content}


def file_to_tiptap_json(filename: str, raw_bytes: bytes) -> str:
    """Entry point: decode bytes and return a TipTap document as a JSON string.

    Raises ValueError for unsupported extensions.
    """
    lower = filename.lower()
    if not lower.endswith(SUPPORTED_EXTENSIONS):
        raise ValueError(
            "Unsupported file type. Only .txt and .md are supported."
        )

    text = raw_bytes.decode("utf-8", errors="replace")

    if lower.endswith(".md"):
        doc = markdown_to_tiptap(text)
    else:
        doc = _plain_text_doc(text)

    return json.dumps(doc)
