"""
Security Utilities

Handles password hashing, JWT tokens, and OAuth support.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token (typically {"sub": user_id})
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: Data to encode in the token (typically {"sub": user_id})
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to get current user ID from JWT token
    
    Usage:
        @app.get("/protected")
        def protected_route(user_id: str = Depends(get_current_user_id)):
            return {"user_id": user_id}
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


# OAuth helper functions (for future Google OAuth implementation)

def generate_oauth_state() -> str:
    """Generate a random state for OAuth flow"""
    import secrets
    return secrets.token_urlsafe(32)


def create_oauth_user_token(user_id: str, oauth_provider: str, oauth_id: str) -> str:
    """
    Create a token for OAuth-authenticated users
    
    Args:
        user_id: User's UUID
        oauth_provider: OAuth provider (e.g., "google")
        oauth_id: Provider's user ID
        
    Returns:
        JWT token
    """
    data = {
        "sub": user_id,
        "oauth_provider": oauth_provider,
        "oauth_id": oauth_id
    }
    return create_access_token(data)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=None  # Will be injected by FastAPI dependency
):
    """
    Dependency to get current user from JWT token
    
    Returns full User object from database.
    
    Usage:
        from app.utils.database import get_db
        from app.models.user import User
        
        @app.get("/protected")
        def protected_route(
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            return {"user": current_user.username}
    """
    from sqlalchemy.orm import Session
    from app.utils.database import get_db as _get_db
    from app.models.user import User
    from uuid import UUID
    
    # Get database session if not provided
    if db is None:
        db = next(_get_db())
    
    # Get user ID from token
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Query user from database
    user = db.query(User).filter(User.id == UUID(user_id_str)).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

