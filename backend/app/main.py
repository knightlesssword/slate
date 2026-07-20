"""Slate API entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import Base, engine
from .routers import auth, documents

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist. Seeding is a separate explicit step (python -m app.seed).
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Slate API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
