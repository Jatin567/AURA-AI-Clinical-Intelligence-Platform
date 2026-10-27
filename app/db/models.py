import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    pass

class TriageSession(Base):
    __tablename__ = "triage_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    intake_stage: Mapped[str] = mapped_column(String(50))
    triage_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    triage_label: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Denormalized flags for fast queries
    had_emergency: Mapped[bool] = mapped_column(Boolean, default=False)
    had_crisis_flag: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    audit_logs: Mapped[list["TriageAuditLog"]] = relationship(back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_triage_sessions_created_at", "created_at"),
    )

class TriageAuditLog(Base):
    __tablename__ = "triage_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("triage_sessions.id", ondelete="CASCADE"))
    event_type: Mapped[str] = mapped_column(String(100))
    event_data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    classification_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    session: Mapped["TriageSession"] = relationship(back_populates="audit_logs")

    __table_args__ = (
        Index("ix_triage_audit_logs_session_id", "session_id"),
        Index("ix_triage_audit_logs_event_type", "event_type"),
    )
