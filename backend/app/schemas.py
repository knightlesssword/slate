"""Pydantic request/response schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    token: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    display_name: str


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content_json: str = ""

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title must not be empty")
        return v


class DocumentUpdate(BaseModel):
    """Partial update: title and/or content_json."""

    title: str | None = Field(default=None, max_length=255)
    content_json: str | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Title must not be empty")
        return v


class DocumentSummary(BaseModel):
    """List view: no heavy content payload."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    owner_id: int
    owner_email: EmailStr
    is_owner: bool
    updated_at: datetime


class DocumentDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content_json: str
    owner_id: int
    owner_email: EmailStr
    is_owner: bool
    shared_with: list[UserOut] = []
    created_at: datetime
    updated_at: datetime


class ShareRequest(BaseModel):
    email: EmailStr
