import json
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import SessionLocal, Bookmark, Summary, Tag, User, Base
from pydantic import BaseModel, Field
from ai_service import summarize_text, generate_tags

router = APIRouter()

# Dependency to get a DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Pydantic schemas (simple, no complex validators)
# ---------------------------------------------------------------------------
class BookmarkCreate(BaseModel):
    url: str = Field(..., description="URL to bookmark")
    title: Optional[str] = Field(None, description="Optional title")
    tags: Optional[List[str]] = Field(default_factory=list, description="Initial tags")
    notes: Optional[str] = Field(None, description="User notes")

class BookmarkResponse(BaseModel):
    bookmark_id: str
    url: str
    title: Optional[str]
    summary: Optional[str]
    tags: List[str] = Field(default_factory=list)
    created_at: str

class SummarizeRequest(BaseModel):
    text: str = Field(..., description="Text to summarize")

class SummarizeResponse(BaseModel):
    summary: str

# ---------------------------------------------------------------------------
# Helper – fetch a dummy user (for the demo we create a single placeholder user)
# ---------------------------------------------------------------------------
def get_demo_user(db: Session) -> User:
    user = db.query(User).first()
    if not user:
        user = User(
            username="demo_user",
            email="demo@example.com",
            password_hash="not_used",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# ---------------------------------------------------------------------------
# Endpoint: Create Bookmark (AI summary + smart tags)
# ---------------------------------------------------------------------------
@router.post("/bookmarks", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(payload: BookmarkCreate, db: Session = Depends(get_db)):
    # Basic validation – URL must be non‑empty string (more robust validation can be added)
    if not payload.url:
        raise HTTPException(status_code=400, detail="URL is required")

    demo_user = get_demo_user(db)

    # Store bookmark record (without summary yet)
    bookmark = Bookmark(
        user_id=demo_user.user_id,
        url=payload.url,
        title=payload.title,
        notes=payload.notes,
    )
    db.add(bookmark)
    db.flush()  # Obtain bookmark_id before committing

    # -------------------------------------------------------------------
    # AI Summarization (calls DO inference)
    # -------------------------------------------------------------------
    summary_result = await summarize_text(payload.url)
    summary_content = summary_result.get("summary") or summary_result.get("note") or ""
    summary = Summary(
        bookmark_id=bookmark.bookmark_id,
        content=summary_content,
        confidence_score=summary_result.get("confidence_score"),
    )
    db.add(summary)

    # -------------------------------------------------------------------
    # AI Tag generation (optional – we also accept client‑provided tags)
    # -------------------------------------------------------------------
    # Combine provided tags with AI‑generated ones (deduplicate later)
    ai_tags_res = await generate_tags(payload.url)
    ai_tags = []
    if isinstance(ai_tags_res, dict) and "tags" in ai_tags_res:
        ai_tags = ai_tags_res["tags"]
    elif isinstance(ai_tags_res, list):
        ai_tags = ai_tags_res
    combined_tags = list(set((payload.tags or []) + ai_tags))

    # Persist tags (create if not exist for the demo user)
    tag_objects: List[Tag] = []
    for tag_name in combined_tags:
        tag = db.query(Tag).filter_by(name=tag_name, user_id=demo_user.user_id).first()
        if not tag:
            tag = Tag(user_id=demo_user.user_id, name=tag_name)
            db.add(tag)
            db.flush()
        tag_objects.append(tag)
    # Associate tags with bookmark (SQLAlchemy many‑to‑many)
    if tag_objects:
        bookmark.tags = tag_objects

    db.commit()
    db.refresh(bookmark)
    db.refresh(summary)

    return BookmarkResponse(
        bookmark_id=bookmark.bookmark_id,
        url=bookmark.url,
        title=bookmark.title,
        summary=summary.content,
        tags=[t.name for t in bookmark.tags] if bookmark.tags else [],
        created_at=bookmark.created_at.isoformat(),
    )

# ---------------------------------------------------------------------------
# Endpoint: Retrieve a Bookmark (includes its summary)
# ---------------------------------------------------------------------------
@router.get("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
def get_bookmark(bookmark_id: str, db: Session = Depends(get_db)):
    bm = db.query(Bookmark).filter_by(bookmark_id=bookmark_id).first()
    if not bm:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    summary_text = bm.summary.content if bm.summary else None
    return BookmarkResponse(
        bookmark_id=bm.bookmark_id,
        url=bm.url,
        title=bm.title,
        summary=summary_text,
        tags=[t.name for t in bm.tags] if bm.tags else [],
        created_at=bm.created_at.isoformat(),
    )

# ---------------------------------------------------------------------------
# Endpoint: Stand‑alone Summarization (raw text)
# ---------------------------------------------------------------------------
@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_endpoint(req: SummarizeRequest):
    result = await summarize_text(req.text)
    # The AI service may return a dict with a "summary" key or a fallback note.
    summary = result.get("summary") or result.get("note") or ""
    return SummarizeResponse(summary=summary)

# ---------------------------------------------------------------------------
# Endpoint: Simple Search (placeholder – returns titles that contain the query)
# ---------------------------------------------------------------------------
@router.get("/search", response_model=List[BookmarkResponse])
def search(q: str = Query(..., description="Search query"), db: Session = Depends(get_db)):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    bms = (
        db.query(Bookmark)
        .filter(Bookmark.title.ilike(f"%{q}%") | Bookmark.url.ilike(f"%{q}%"))
        .limit(20)
        .all()
    )
    response = []
    for bm in bms:
        response.append(
            BookmarkResponse(
                bookmark_id=bm.bookmark_id,
                url=bm.url,
                title=bm.title,
                summary=bm.summary.content if bm.summary else None,
                tags=[t.name for t in bm.tags] if bm.tags else [],
                created_at=bm.created_at.isoformat(),
            )
        )
    return response
