"""
Authentication API

Handles user registration, login, and token management.
Designed to support Google OAuth in the future.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user_id
)
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.models.user import User, AuthProvider

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with email and password.
    
    Future: Will support OAuth registration too.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        auth_provider=AuthProvider.EMAIL,
        is_active=True,
        is_verified=False  # Could implement email verification later
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.from_orm(new_user)
    )


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password.
    
    Returns access token and refresh token.
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not user.password_hash or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.from_orm(user)
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    # Decode refresh token
    payload = decode_token(refresh_token)
    
    # Verify it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Get current authenticated user information.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)


# Google OAuth endpoints
from fastapi.responses import RedirectResponse, JSONResponse
from app.services.google_oauth import get_oauth_service
from datetime import datetime


@router.get("/google/login")
def google_oauth_login():
    """
    Initiate Google OAuth flow.
    Returns authorization URL for client to redirect to.
    """
    oauth_service = get_oauth_service()
    authorization_url, state = oauth_service.get_authorization_url()
    
    return {
        "authorization_url": authorization_url,
        "state": state
    }


@router.get("/google/callback")
def google_oauth_callback(
    code: str,
    state: str = None,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback.
    Exchanges code for tokens and creates/updates user.
    """
    oauth_service = get_oauth_service()
    
    try:
        # Exchange code for tokens
        tokens = oauth_service.exchange_code_for_tokens(code)
        
        # Get user info from Google
        user_info = oauth_service.get_user_info(tokens["access_token"])
        
        # Find existing user by Google ID or email
        user = db.query(User).filter(
            (User.oauth_id == user_info["google_id"]) | 
            (User.email == user_info["email"])
        ).first()
        
        if user:
            # Update existing user with OAuth tokens
            user.auth_provider = AuthProvider.GOOGLE
            user.oauth_id = user_info["google_id"]
            user.google_access_token = tokens["access_token"]
            user.google_refresh_token = tokens.get("refresh_token")  # May be None if already exists
            user.google_token_expires_at = tokens["expires_at"]
            user.full_name = user_info["name"]
            user.profile_picture_url = user_info["picture"]
            user.is_verified = user_info["verified_email"]
            user.last_login_at = datetime.utcnow()
            
            # Update refresh token only if we got a new one
            if tokens.get("refresh_token"):
                user.google_refresh_token = tokens["refresh_token"]
        else:
            # Create new user
            # Generate username from email
            username = user_info["email"].split("@")[0]
            # Make username unique if it already exists
            base_username = username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User(
                email=user_info["email"],
                username=username,
                password_hash=None,  # OAuth users don't have password
                auth_provider=AuthProvider.GOOGLE,
                oauth_id=user_info["google_id"],
                google_access_token=tokens["access_token"],
                google_refresh_token=tokens.get("refresh_token"),
                google_token_expires_at=tokens["expires_at"],
                full_name=user_info["name"],
                profile_picture_url=user_info["picture"],
                is_verified=user_info["verified_email"],
                is_active=True,
                last_login_at=datetime.utcnow()
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
        
        # Create JWT token for our app
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # Redirect to frontend with token
        frontend_url = "http://localhost:5173"
        redirect_url = f"{frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
        
        return RedirectResponse(url=redirect_url, status_code=302)
        
    except Exception as e:
        # Redirect to frontend with error
        frontend_url = "http://localhost:5173"
        error_url = f"{frontend_url}/login?error=oauth_failed&message={str(e)}"
        return RedirectResponse(url=error_url, status_code=302)

