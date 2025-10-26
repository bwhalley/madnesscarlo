"""
Google OAuth Service

Handles Google OAuth 2.0 authentication flow including:
- Authorization URL generation
- Token exchange
- User profile fetching
- Token refresh
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class GoogleOAuthService:
    """Service for handling Google OAuth operations"""
    
    # OAuth scopes we need
    SCOPES = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    def _get_flow(self) -> Flow:
        """Create a Google OAuth flow"""
        return Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": [self.redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
    
    def get_authorization_url(self, state: str = None) -> tuple[str, str]:
        """
        Generate Google OAuth authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
        
        Returns:
            Tuple of (authorization_url, state)
        """
        flow = self._get_flow()
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',  # Get refresh token
            include_granted_scopes='true',
            prompt='consent'  # Force consent screen to always get refresh token
        )
        
        logger.info(f"Generated OAuth authorization URL with state: {state}")
        return authorization_url, state
    
    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from Google
        
        Returns:
            Dictionary with tokens and expiration info
        """
        flow = self._get_flow()
        
        try:
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            logger.info("Successfully exchanged authorization code for tokens")
            
            return {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "expires_at": credentials.expiry,
                "scopes": credentials.scopes
            }
        except Exception as e:
            logger.error(f"Failed to exchange code for tokens: {e}")
            raise
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user profile information from Google.
        
        Args:
            access_token: Google access token
        
        Returns:
            Dictionary with user profile data
        """
        try:
            credentials = Credentials(token=access_token)
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            
            logger.info(f"Retrieved user info for email: {user_info.get('email')}")
            
            return {
                "google_id": user_info.get("id"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "verified_email": user_info.get("verified_email", False)
            }
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            raise
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token using a refresh token.
        
        Args:
            refresh_token: Google refresh token
        
        Returns:
            Dictionary with new access token and expiration
        """
        try:
            from google.auth.transport.requests import Request
            
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            credentials.refresh(Request())
            
            logger.info("Successfully refreshed access token")
            
            return {
                "access_token": credentials.token,
                "expires_at": credentials.expiry
            }
        except Exception as e:
            logger.error(f"Failed to refresh access token: {e}")
            raise
    
    def is_token_expired(self, expires_at: datetime) -> bool:
        """
        Check if a token is expired or about to expire.
        
        Args:
            expires_at: Token expiration datetime
        
        Returns:
            True if token is expired or expires in < 5 minutes
        """
        if not expires_at:
            return True
        
        # Add 5 minute buffer
        expiry_buffer = datetime.now(expires_at.tzinfo) + timedelta(minutes=5)
        return expires_at <= expiry_buffer


# Singleton instance
_oauth_service = None


def get_oauth_service() -> GoogleOAuthService:
    """Get singleton instance of GoogleOAuthService"""
    global _oauth_service
    if _oauth_service is None:
        _oauth_service = GoogleOAuthService()
    return _oauth_service

