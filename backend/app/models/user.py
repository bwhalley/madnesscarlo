"""
User Model

Handles user authentication with support for:
- Email/password authentication
- OAuth providers (Google, etc.) - future support
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.utils.database import Base


class AuthProvider(str, enum.Enum):
    """Authentication provider types"""
    EMAIL = "email"
    GOOGLE = "google"
    # Future: GITHUB = "github", etc.


class User(Base):
    """User account model"""
    __tablename__ = "users"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Null for OAuth users
    
    # OAuth support
    auth_provider = Column(SQLEnum(AuthProvider), nullable=False, default=AuthProvider.EMAIL)
    oauth_id = Column(String(255), nullable=True, index=True)  # Provider's user ID
    
    # Google OAuth tokens (for API access)
    google_access_token = Column(Text, nullable=True)  # Access token for Google APIs
    google_refresh_token = Column(Text, nullable=True)  # Refresh token to get new access tokens
    google_token_expires_at = Column(DateTime(timezone=True), nullable=True)  # When access token expires
    
    # Profile
    full_name = Column(String(100), nullable=True)
    profile_picture_url = Column(String(500), nullable=True)  # Google profile picture
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"

