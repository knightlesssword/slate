"""Document routes: CRUD, rename, import, share."""
import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from ..config import get_settings
from ..crud import (
    get_user_by_email,
    list_documents_for_user,
    shared_users,
    user_can_access,
)
from ..database import get_db
from ..deps import get_current_user
from ..importer import file_to_tiptap_json
from ..models import Document, Share, User
from ..schemas import (
    DocumentCreate,
    DocumentDetail,
    DocumentSummary,
    DocumentUpdate,
    ShareRequest,
    UserOut,
)

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()


def _load_document_or_404(db: Session, document_id: int) -> Document:
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return doc


def _require_access(db: Session, doc: Document, user: User) -> None:
    if not user_can_access(db, doc, user):
        # 403: authenticated but not permitted.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this document",
        )


def _summary(doc: Document, user: User) -> DocumentSummary:
    return DocumentSummary(
        id=doc.id,
        title=doc.title,
        owner_id=doc.owner_id,
        owner_email=doc.owner.email,
        is_owner=doc.owner_id == user.id,
        updated_at=doc.updated_at,
    )


def _detail(db: Session, doc: Document, user: User) -> DocumentDetail:
    is_owner = doc.owner_id == user.id
    return DocumentDetail(
        id=doc.id,
        title=doc.title,
        content_json=doc.content_json,
        owner_id=doc.owner_id,
        owner_email=doc.owner.email,
        is_owner=is_owner,
        shared_with=[UserOut.model_validate(u) for u in shared_users(db, doc)]
        if is_owner
        else [],
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.get("", response_model=list[DocumentSummary])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DocumentSummary]:
    docs = list_documents_for_user(db, current_user)
    return [_summary(d, current_user) for d in docs]


@router.post("", response_model=DocumentDetail, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentDetail:
    doc = Document(
        owner_id=current_user.id,
        title=payload.title,
        content_json=payload.content_json,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return _detail(db, doc, current_user)


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentDetail:
    doc = _load_document_or_404(db, document_id)
    _require_access(db, doc, current_user)
    return _detail(db, doc, current_user)


@router.put("/{document_id}", response_model=DocumentDetail)
def update_document(
    document_id: int,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentDetail:
    doc = _load_document_or_404(db, document_id)
    _require_access(db, doc, current_user)

    if payload.title is not None:
        doc.title = payload.title
    if payload.content_json is not None:
        doc.content_json = payload.content_json

    db.commit()
    db.refresh(doc)
    return _detail(db, doc, current_user)


@router.post(
    "/import",
    response_model=DocumentDetail,
    status_code=status.HTTP_201_CREATED,
)
async def import_document(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentDetail:
    raw = await file.read()
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File is too large (max ~1 MB).",
        )

    try:
        content_json = file_to_tiptap_json(file.filename or "", raw)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    # Default the title from the filename if none supplied.
    doc_title = (title or "").strip()
    if not doc_title:
        base = (file.filename or "Imported document").rsplit(".", 1)[0]
        doc_title = base.strip() or "Imported document"

    doc = Document(
        owner_id=current_user.id,
        title=doc_title[:255],
        content_json=content_json,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return _detail(db, doc, current_user)


@router.post("/{document_id}/share", response_model=DocumentDetail)
def share_document(
    document_id: int,
    payload: ShareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentDetail:
    doc = _load_document_or_404(db, document_id)

    # Only the owner may manage sharing.
    if doc.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can share this document",
        )

    target = get_user_by_email(db, payload.email)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with that email",
        )
    if target.id == doc.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already own this document",
        )

    existing = (
        db.query(Share)
        .filter(Share.document_id == doc.id, Share.user_id == target.id)
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document is already shared with that user",
        )

    db.add(Share(document_id=doc.id, user_id=target.id))
    db.commit()
    db.refresh(doc)
    return _detail(db, doc, current_user)
