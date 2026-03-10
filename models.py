import os
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Text,
    Float,
    ForeignKey,
    create_engine,
    inspect,
    Index,
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

# ---------------------------------------------------------------------------
# Database URL handling (shared DB – prefix tables with "ls_")
# ---------------------------------------------------------------------------
_raw_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or "sqlite:///./app.db"
# Normalise possible scheme variants
if _raw_url.startswith("postgresql+asyncpg://"):
    _raw_url = _raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql+psycopg://")

# Determine if we need SSL (non‑localhost & non‑sqlite)
_connect_args = {}
if not _raw_url.startswith("sqlite") and "localhost" not in _raw_url and "127.0.0.1" not in _raw_url:
    _connect_args["sslmode"] = "require"

engine = create_engine(_raw_url, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

# ---------------------------------------------------------------------------
# Models (all table names prefixed with "ls_")
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "ls_users"
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    bookmarks = relationship("Bookmark", back_populates="owner")

class Bookmark(Base):
    __tablename__ = "ls_bookmarks"
    bookmark_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("ls_users.user_id"), nullable=False)
    url = Column(String(1000), nullable=False)
    title = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    is_private = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="bookmarks")
    summary = relationship("Summary", back_populates="bookmark", uselist=False)
    tags = relationship("Tag", secondary="ls_bookmark_tags", back_populates="bookmarks")

class Summary(Base):
    __tablename__ = "ls_summaries"
    summary_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bookmark_id = Column(String, ForeignKey("ls_bookmarks.bookmark_id"), nullable=False, unique=True)
    content = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)
    status = Column(String(20), default="completed", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    bookmark = relationship("Bookmark", back_populates="summary")

class Tag(Base):
    __tablename__ = "ls_tags"
    tag_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("ls_users.user_id"), nullable=False)
    name = Column(String(50), nullable=False)
    color = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    bookmarks = relationship("Bookmark", secondary="ls_bookmark_tags", back_populates="tags")

# Association table for many‑to‑many Bookmark‑Tag relationship
from sqlalchemy import Table
ls_bookmark_tags = Table(
    "ls_bookmark_tags",
    Base.metadata,
    Column("bookmark_id", String, ForeignKey("ls_bookmarks.bookmark_id"), primary_key=True),
    Column("tag_id", String, ForeignKey("ls_tags.tag_id"), primary_key=True),
    Index("ix_ls_bookmark_tags_bookmark_id", "bookmark_id"),
    Index("ix_ls_bookmark_tags_tag_id", "tag_id"),
)

# Create all tables if they don't exist (useful for the demo environment)
if not inspect(engine).has_table("ls_users"):
    Base.metadata.create_all(bind=engine)
