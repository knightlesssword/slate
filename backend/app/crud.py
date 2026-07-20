"""Data-access helpers, including the document access-control rule.

The access rule lives here (and is unit-tested) so it is a single source of
truth: a user may read/edit a document if they are the owner OR the document has
been shared with them. Everyone else is denied.
"""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .models import Document, Share, User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def user_can_access(db: Session, document: Document, user: User) -> bool:
    if document.owner_id == user.id:
        return True
    share = db.scalar(
        select(Share).where(
            Share.document_id == document.id, Share.user_id == user.id
        )
    )
    return share is not None


def list_documents_for_user(db: Session, user: User) -> list[Document]:
    """Owned documents plus documents shared with the user, newest first."""
    shared_ids = select(Share.document_id).where(Share.user_id == user.id)
    stmt = (
        select(Document)
        .where(or_(Document.owner_id == user.id, Document.id.in_(shared_ids)))
        .order_by(Document.updated_at.desc())
    )
    return list(db.scalars(stmt))


def shared_users(db: Session, document: Document) -> list[User]:
    stmt = (
        select(User)
        .join(Share, Share.user_id == User.id)
        .where(Share.document_id == document.id)
        .order_by(User.display_name)
    )
    return list(db.scalars(stmt))
