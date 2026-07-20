"""Seed the database with demo users (idempotent).

Run: python -m app.seed
"""
from sqlalchemy import select

from .crud import get_user_by_email
from .database import Base, SessionLocal, engine
from .models import Document, User
from .security import hash_password

SEED_USERS = [
    {"email": "alice@example.com", "display_name": "Alice", "password": "password123"},
    {"email": "bob@example.com", "display_name": "Bob", "password": "password123"},
    {"email": "carol@example.com", "display_name": "Carol", "password": "password123"},
]

WELCOME_DOC = {
    "type": "doc",
    "content": [
        {"type": "heading", "attrs": {"level": 1},
         "content": [{"type": "text", "text": "Welcome to Slate"}]},
        {"type": "paragraph", "content": [
            {"type": "text", "text": "This is a sample document owned by Alice. "},
            {"type": "text", "marks": [{"type": "bold"}], "text": "Bold"},
            {"type": "text", "text": ", "},
            {"type": "text", "marks": [{"type": "italic"}], "text": "italic"},
            {"type": "text", "text": ", and "},
            {"type": "text", "marks": [{"type": "underline"}], "text": "underline"},
            {"type": "text", "text": " all work."},
        ]},
        {"type": "bulletList", "content": [
            {"type": "listItem", "content": [
                {"type": "paragraph", "content": [
                    {"type": "text", "text": "Create and rename documents"}]}]},
            {"type": "listItem", "content": [
                {"type": "paragraph", "content": [
                    {"type": "text", "text": "Import a .txt or .md file"}]}]},
            {"type": "listItem", "content": [
                {"type": "paragraph", "content": [
                    {"type": "text", "text": "Share with another user"}]}]},
        ]},
    ],
}


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for spec in SEED_USERS:
            if get_user_by_email(db, spec["email"]) is None:
                db.add(User(
                    email=spec["email"],
                    display_name=spec["display_name"],
                    password_hash=hash_password(spec["password"]),
                ))
        db.commit()

        alice = get_user_by_email(db, "alice@example.com")
        has_doc = db.scalar(
            select(Document).where(Document.owner_id == alice.id)
        )
        if has_doc is None:
            import json
            db.add(Document(
                owner_id=alice.id,
                title="Welcome to Slate",
                content_json=json.dumps(WELCOME_DOC),
            ))
            db.commit()

        print("Seed complete. Demo users:")
        for spec in SEED_USERS:
            print(f"  {spec['email']} / {spec['password']}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
