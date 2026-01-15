"""
AuthSession model for storing user authentication sessions.
This file should be in: app/models/auth_sessions.py
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.routers import users
from app.models.base import Base
from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship


if TYPE_CHECKING:
    from app.models.users import User



class AuthSession(Base):
    """Model for storing user authentication refresh tokens and sessions."""
    
    __tablename__ = "auth_sessions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign key to users table
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Refresh token (hashed)
    refresh_token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Device information
    device_name: Mapped[str | None] = mapped_column(String(255))
    device_id: Mapped[str | None] = mapped_column(String(255))
    
    # Request information
    ip_address: Mapped[str | None] = mapped_column(String(45))  # IPv6 max length
    user_agent: Mapped[str | None] = mapped_column(String(500))
    
    # Session status
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    
    # Relationship to User model
    user: Mapped["User"] = relationship("User", back_populates="auth_sessions")
    
    def __repr__(self):
        return f"<AuthSession(id={self.id}, user_id={self.user_id}, revoked={self.is_revoked})>"