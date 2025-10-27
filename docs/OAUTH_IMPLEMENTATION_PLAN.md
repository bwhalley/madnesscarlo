# 🔐 Google OAuth Implementation Plan

## Overview

We're implementing Google OAuth to allow users to:
1. **Sign in with Google** (replacing/augmenting email/password)
2. **Export simulations to their own Google Drive** (bypassing organization restrictions)

This solves the organization policy issue AND provides better UX!

---

## 🎯 What We're Building

### User Flow

```
1. User clicks "Sign in with Google"
   ↓
2. Redirected to Google login page
   ↓
3. User grants permissions (Drive + Sheets access)
   ↓
4. Google redirects back with authorization code
   ↓
5. Backend exchanges code for access token + refresh token
   ↓
6. Tokens stored in database (encrypted)
   ↓
7. User is logged in!
   ↓
8. Later: User clicks "Export to Google Sheets"
   ↓
9. Backend uses user's OAuth token
   ↓
10. Sheet created in USER'S Google Drive!
```

---

## 📋 Implementation Phases

### Phase 1: Google Cloud Setup (30 minutes)
- Create OAuth 2.0 credentials
- Configure consent screen
- Set redirect URIs

### Phase 2: Database Schema (15 minutes)
- Add OAuth token storage to User model
- Create migration

### Phase 3: Backend OAuth Flow (2 hours)
- OAuth endpoints (login, callback)
- Token storage and encryption
- Google API integration

### Phase 4: Frontend OAuth UI (1 hour)
- "Sign in with Google" button
- OAuth redirect handling
- Token status display

### Phase 5: Sheets Export with OAuth (1 hour)
- Update export endpoint to use user tokens
- Handle token refresh
- Error handling

### Phase 6: Testing & Polish (1 hour)
- Test full flow
- Error handling
- UI polish

**Total Time: ~5-7 hours**

---

## 🔧 Phase 1: Google Cloud Setup

### Step 1.1: Create OAuth 2.0 Credentials

```bash
# Go to Google Cloud Console
# https://console.cloud.google.com/apis/credentials?project=madness-carlo-local

# OR create via CLI:
gcloud auth application-default login

# Note: We'll use the web console for OAuth setup
```

### Step 1.2: Configure OAuth Consent Screen

1. Go to: https://console.cloud.google.com/apis/credentials/consent?project=madness-carlo-local

2. Choose **"External"** (allows any Google user)

3. Fill in:
   - **App name**: Madness Carlo Simulator
   - **User support email**: your-email@example.com
   - **Developer contact**: your-email@example.com

4. **Scopes**: Add these:
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
   - `https://www.googleapis.com/auth/drive.file`
   - `https://www.googleapis.com/auth/spreadsheets`

5. Save

### Step 1.3: Create OAuth Client ID

1. Go to: https://console.cloud.google.com/apis/credentials?project=madness-carlo-local

2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**

3. Choose **"Web application"**

4. Name: `Madness Carlo Web App`

5. **Authorized redirect URIs**:
   - `http://localhost:8000/api/auth/google/callback` (development)
   - `http://localhost:5173/auth/callback` (frontend development)
   - (Add production URLs later)

6. Click **Create**

7. **Save these values**:
   ```
   Client ID: YOUR_CLIENT_ID_HERE.apps.googleusercontent.com
   Client Secret: YOUR_CLIENT_SECRET_HERE
   ```

---

## 🗄️ Phase 2: Database Schema

### Step 2.1: Update User Model

Add OAuth fields to the User model:

```python
# backend/app/models/user.py

class User(Base):
    __tablename__ = "users"
    
    # Existing fields...
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Make nullable for OAuth users
    
    # NEW: OAuth fields
    google_id = Column(String, unique=True, nullable=True, index=True)
    google_access_token = Column(Text, nullable=True)  # Encrypted
    google_refresh_token = Column(Text, nullable=True)  # Encrypted
    google_token_expires_at = Column(DateTime, nullable=True)
    
    # Profile info from Google
    google_profile_picture = Column(String, nullable=True)
    google_name = Column(String, nullable=True)
```

### Step 2.2: Create Migration

```bash
# In backend directory
docker exec -it madness-backend bash

# Generate migration
alembic revision --autogenerate -m "Add Google OAuth fields to User model"

# Review migration in backend/alembic/versions/

# Run migration
alembic upgrade head
```

---

## 🔒 Phase 3: Backend OAuth Implementation

### Step 3.1: Add OAuth Configuration

```python
# backend/app/config.py

class Settings(BaseSettings):
    # Existing settings...
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    
    # OAuth scopes
    GOOGLE_SCOPES: list = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/spreadsheets",
    ]
```

### Step 3.2: Create OAuth Service

```python
# backend/app/services/google_oauth.py

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json
from datetime import datetime, timedelta

class GoogleOAuthService:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state: str = None) -> str:
        """Generate Google OAuth authorization URL"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": [self.redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=settings.GOOGLE_SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',  # Get refresh token
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )
        
        return authorization_url, state
    
    def exchange_code_for_tokens(self, code: str):
        """Exchange authorization code for access and refresh tokens"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": [self.redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=settings.GOOGLE_SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_at": credentials.expiry,
            "scopes": credentials.scopes
        }
    
    def get_user_info(self, access_token: str):
        """Get user profile info from Google"""
        credentials = Credentials(token=access_token)
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        return {
            "google_id": user_info.get("id"),
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "verified_email": user_info.get("verified_email")
        }
    
    def refresh_access_token(self, refresh_token: str):
        """Refresh an expired access token"""
        # Implementation for token refresh
        pass
```

### Step 3.3: Create OAuth Endpoints

```python
# backend/app/api/auth.py (add to existing file)

from app.services.google_oauth import GoogleOAuthService

google_oauth_service = GoogleOAuthService(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    redirect_uri=settings.GOOGLE_REDIRECT_URI
)

@router.get("/google/login")
def google_login():
    """
    Initiate Google OAuth flow.
    Redirects user to Google login page.
    """
    authorization_url, state = google_oauth_service.get_authorization_url()
    
    # Store state in session or database for security
    # For now, we'll just return the URL
    
    return {
        "authorization_url": authorization_url,
        "state": state
    }

@router.get("/google/callback")
def google_callback(
    code: str,
    state: str = None,
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback from Google.
    Exchanges code for tokens and creates/updates user.
    """
    # Exchange code for tokens
    tokens = google_oauth_service.exchange_code_for_tokens(code)
    
    # Get user info from Google
    user_info = google_oauth_service.get_user_info(tokens["access_token"])
    
    # Find or create user
    user = db.query(User).filter(User.google_id == user_info["google_id"]).first()
    
    if not user:
        # Create new user
        user = User(
            email=user_info["email"],
            google_id=user_info["google_id"],
            google_name=user_info["name"],
            google_profile_picture=user_info["picture"],
            hashed_password=None  # OAuth users don't need password
        )
        db.add(user)
    
    # Update OAuth tokens (encrypted in production!)
    user.google_access_token = tokens["access_token"]
    user.google_refresh_token = tokens["refresh_token"]
    user.google_token_expires_at = tokens["expires_at"]
    
    db.commit()
    db.refresh(user)
    
    # Create JWT for our app
    access_token = create_access_token(data={"sub": user.email})
    
    # Redirect to frontend with token
    return RedirectResponse(
        url=f"http://localhost:5173/auth/callback?token={access_token}",
        status_code=302
    )
```

---

## 🎨 Phase 4: Frontend OAuth UI

### Step 4.1: Add Google Login Button

```typescript
// frontend/src/components/GoogleLoginButton.tsx

import { useState } from 'react';

export function GoogleLoginButton() {
  const [loading, setLoading] = useState(false);

  const handleGoogleLogin = async () => {
    setLoading(true);
    try {
      // Get authorization URL from backend
      const response = await fetch('http://localhost:8000/api/auth/google/login');
      const data = await response.json();
      
      // Redirect to Google
      window.location.href = data.authorization_url;
    } catch (error) {
      console.error('Error initiating Google login:', error);
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleGoogleLogin}
      disabled={loading}
      className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
    >
      <svg className="w-5 h-5" viewBox="0 0 24 24">
        <path
          fill="#4285F4"
          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        />
        <path
          fill="#34A853"
          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        />
        <path
          fill="#FBBC05"
          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        />
        <path
          fill="#EA4335"
          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        />
      </svg>
      {loading ? 'Redirecting...' : 'Sign in with Google'}
    </button>
  );
}
```

### Step 4.2: Add OAuth Callback Handler

```typescript
// frontend/src/pages/AuthCallback.tsx

import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authService } from '../services/auth';

export function AuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (token) {
      // Store token
      localStorage.setItem('token', token);
      
      // Redirect to dashboard
      navigate('/');
    } else {
      // Error - redirect to login
      navigate('/login?error=oauth_failed');
    }
  }, [searchParams, navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Completing sign in...</p>
      </div>
    </div>
  );
}
```

### Step 4.3: Update AuthForm to Include Google Login

```typescript
// frontend/src/components/AuthForm.tsx

import { GoogleLoginButton } from './GoogleLoginButton';

// In the form JSX:
<div className="space-y-4">
  {/* Google Login */}
  <GoogleLoginButton />
  
  {/* Divider */}
  <div className="relative">
    <div className="absolute inset-0 flex items-center">
      <div className="w-full border-t border-gray-300"></div>
    </div>
    <div className="relative flex justify-center text-sm">
      <span className="px-2 bg-white text-gray-500">Or continue with email</span>
    </div>
  </div>
  
  {/* Existing email/password form */}
  ...
</div>
```

---

## 📊 Phase 5: Google Sheets Export with OAuth

### Step 5.1: Create OAuth Sheets Service

```python
# backend/app/services/google_sheets_oauth.py

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

class GoogleSheetsOAuthService:
    """Service for exporting simulations using user's OAuth tokens"""
    
    def export_simulation(
        self,
        access_token: str,
        simulation_data: dict,
        deck_name: str
    ):
        """
        Export simulation to user's Google Drive using their OAuth token.
        
        This creates the spreadsheet in the USER's Drive, not a service account!
        """
        # Create credentials from user's access token
        credentials = Credentials(token=access_token)
        
        # Build Sheets API service
        sheets_service = build('sheets', 'v4', credentials=credentials)
        
        # Create spreadsheet
        spreadsheet = {
            'properties': {
                'title': f'MTG Simulation - {deck_name} - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            },
            'sheets': [
                {'properties': {'title': 'Summary'}},
                {'properties': {'title': 'Card Statistics'}},
                {'properties': {'title': 'Key Cards'}},
                {'properties': {'title': 'Mulligan Analysis'}}
            ]
        }
        
        spreadsheet = sheets_service.spreadsheets().create(
            body=spreadsheet
        ).execute()
        
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        
        # Populate data (same logic as before, but using user's credentials)
        self._populate_summary(sheets_service, spreadsheet_id, simulation_data)
        self._populate_card_stats(sheets_service, spreadsheet_id, simulation_data)
        # ... etc
        
        return {
            'spreadsheet_id': spreadsheet_id,
            'spreadsheet_url': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}',
            'message': 'Spreadsheet created in your Google Drive!'
        }
```

### Step 5.2: Update Export Endpoint

```python
# backend/app/api/simulations.py

@router.post("/{simulation_id}/export-to-sheets")
def export_simulation_to_sheets(
    simulation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export simulation to user's Google Drive using OAuth."""
    
    # Check if user has connected Google
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please connect your Google account first"
        )
    
    # Check if token is expired
    if current_user.google_token_expires_at < datetime.utcnow():
        # Refresh token
        # ... token refresh logic ...
        pass
    
    # Get simulation
    simulation = db.query(Simulation).filter(
        Simulation.id == UUID(simulation_id),
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    # Export using user's OAuth token
    sheets_service = GoogleSheetsOAuthService()
    result = sheets_service.export_simulation(
        access_token=current_user.google_access_token,
        simulation_data=simulation.results,
        deck_name=simulation.deck.name
    )
    
    return result
```

---

## 🧪 Phase 6: Testing

### Test Checklist

- [ ] User can click "Sign in with Google"
- [ ] Redirected to Google consent screen
- [ ] After approval, redirected back to app
- [ ] User is logged in with JWT token
- [ ] User profile shows Google info
- [ ] User can export simulation
- [ ] Spreadsheet appears in user's Google Drive
- [ ] Spreadsheet has all data and formatting
- [ ] Token refresh works when expired
- [ ] Error handling for denied permissions

---

## 🔐 Security Considerations

### Token Storage

**For Development:**
- Store tokens in database (encrypted recommended but optional)

**For Production:**
- MUST encrypt tokens before storing
- Use environment-specific encryption keys
- Consider using a secrets manager (AWS Secrets Manager, etc.)

### Token Encryption Example

```python
from cryptography.fernet import Fernet

class TokenEncryption:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, token: str) -> str:
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt(self, encrypted_token: str) -> str:
        return self.cipher.decrypt(encrypted_token.encode()).decode()
```

---

## 📝 Environment Variables

Add to `docker-compose.yml`:

```yaml
environment:
  # Existing vars...
  
  # Google OAuth
  - GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE.apps.googleusercontent.com
  - GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
  - GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

---

## 🚀 Deployment Considerations

### Production URLs

Update redirect URIs in Google Cloud Console:
- `https://yourdomain.com/api/auth/google/callback`
- `https://yourdomain.com/auth/callback`

### HTTPS Required

Google OAuth requires HTTPS in production. Options:
- Use Let's Encrypt (free SSL)
- Use Cloudflare (free SSL + CDN)
- Use AWS Certificate Manager

---

## 📚 Documentation to Create

1. **User Guide**: How to connect Google account
2. **Developer Guide**: OAuth flow explanation
3. **Troubleshooting Guide**: Common OAuth issues

---

## ✅ Benefits of This Approach

1. **Bypasses Organization Restrictions** ✅
   - User authenticates with their own account
   - No service account needed
   - Org policies don't apply to user's own permissions

2. **Better UX** ✅
   - Sheets appear in user's Drive automatically
   - Users own their data
   - No sharing/permission management needed

3. **More Secure** ✅
   - No shared credentials
   - Per-user tokens
   - Easy to revoke access

4. **Scalable** ✅
   - Works for unlimited users
   - Each user has their own quota
   - No service account quota limits

---

## 🎯 Ready to Start?

Let's begin with Phase 1: Setting up Google OAuth credentials!

**Next Steps:**
1. Create OAuth credentials in Google Cloud Console
2. Save Client ID and Client Secret
3. Update docker-compose.yml with credentials
4. Begin backend implementation

Let me know when you're ready to start! 🚀

