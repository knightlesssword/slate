"""Test the sharing access rule end to end (PLAN.md success criteria 5-8).

owner shares with grantee -> grantee gets 200, outsider gets 403,
unknown user rejected, duplicate share rejected.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.security import hash_password


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    db = TestingSession()
    for name in ("alice", "bob", "carol"):
        db.add(User(
            email=f"{name}@example.com",
            display_name=name.capitalize(),
            password_hash=hash_password("password123"),
        ))
    db.commit()
    db.close()

    def override_get_db():
        s = TestingSession()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def _login(client, email):
    resp = client.post("/login", json={"email": email, "password": "password123"})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['token']}"}


def test_sharing_access_rule(client):
    alice = _login(client, "alice@example.com")
    bob = _login(client, "bob@example.com")
    carol = _login(client, "carol@example.com")

    # Alice creates a document.
    created = client.post("/documents", json={"title": "Secret plan"}, headers=alice)
    assert created.status_code == 201, created.text
    doc_id = created.json()["id"]

    # Before sharing: Bob and Carol are both forbidden.
    assert client.get(f"/documents/{doc_id}", headers=bob).status_code == 403
    assert client.get(f"/documents/{doc_id}", headers=carol).status_code == 403

    # Alice shares with Bob.
    shared = client.post(
        f"/documents/{doc_id}/share",
        json={"email": "bob@example.com"},
        headers=alice,
    )
    assert shared.status_code == 200, shared.text

    # Now Bob can read (200); Carol still cannot (403).
    assert client.get(f"/documents/{doc_id}", headers=bob).status_code == 200
    assert client.get(f"/documents/{doc_id}", headers=carol).status_code == 403

    # Bob (a grantee) can also edit.
    edit = client.put(
        f"/documents/{doc_id}",
        json={"content_json": "{\"type\":\"doc\"}"},
        headers=bob,
    )
    assert edit.status_code == 200, edit.text


def test_share_validation(client):
    alice = _login(client, "alice@example.com")
    doc_id = client.post(
        "/documents", json={"title": "Doc"}, headers=alice
    ).json()["id"]

    # Unknown user is rejected.
    unknown = client.post(
        f"/documents/{doc_id}/share",
        json={"email": "nobody@example.com"},
        headers=alice,
    )
    assert unknown.status_code == 404

    # First real share succeeds, duplicate is rejected.
    ok = client.post(
        f"/documents/{doc_id}/share",
        json={"email": "bob@example.com"},
        headers=alice,
    )
    assert ok.status_code == 200
    dup = client.post(
        f"/documents/{doc_id}/share",
        json={"email": "bob@example.com"},
        headers=alice,
    )
    assert dup.status_code == 409


def test_non_owner_cannot_share(client):
    alice = _login(client, "alice@example.com")
    bob = _login(client, "bob@example.com")
    doc_id = client.post(
        "/documents", json={"title": "Doc"}, headers=alice
    ).json()["id"]

    # Even after being shared with, Bob cannot re-share (owner-only action).
    client.post(
        f"/documents/{doc_id}/share",
        json={"email": "bob@example.com"},
        headers=alice,
    )
    resp = client.post(
        f"/documents/{doc_id}/share",
        json={"email": "carol@example.com"},
        headers=bob,
    )
    assert resp.status_code == 403
