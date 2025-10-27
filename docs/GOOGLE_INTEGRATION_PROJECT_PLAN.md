# Google OAuth & Sheets Integration - Project Plan

## 🎯 Goal

Add Google OAuth authentication and Google Sheets export functionality to enable users to:
1. **Log in with Google** (alternative to email/password)
2. **Export simulation results** directly to Google Sheets

---

## 📋 Overview

### Current State
- ✅ Email/password authentication (JWT-based)
- ✅ Simulation results stored in PostgreSQL (JSONB)
- ✅ Results displayed in React frontend
- ✅ Original CLI exports to XLSX files

### Target State
- ✅ Google OAuth login (single sign-on)
- ✅ Google Sheets API integration
- ✅ "Export to Google Sheets" button on results page
- ✅ One-click export with proper formatting
- ✅ Link to created spreadsheet

---

## 🏗️ Architecture Overview

```
User Flow:
1. User clicks "Sign in with Google"
2. Google OAuth consent screen
3. User grants permissions
4. Backend receives OAuth token
5. Create/link user account
6. Store refresh token (for Sheets API)

Export Flow:
1. User views simulation results
2. Clicks "Export to Google Sheets"
3. Backend creates spreadsheet via Sheets API
4. Formats data (tabs, charts, colors)
5. Returns spreadsheet URL
6. Frontend shows "Open in Sheets" link
```

---

## 🔐 OAuth Scopes Required

### For Login
- `openid` - OpenID Connect
- `email` - User email address
- `profile` - User profile information

### For Sheets Export
- `https://www.googleapis.com/auth/spreadsheets` - Create and edit spreadsheets
- `https://www.googleapis.com/auth/drive.file` - Access to files created by the app

---

## 📦 Phase 1: Google Cloud Setup

### Tasks

#### 1.1 Create Google Cloud Project
- [ ] Go to https://console.cloud.google.com
- [ ] Create new project: "MTG Madness Carlo"
- [ ] Enable Google+ API
- [ ] Enable Google Sheets API
- [ ] Enable Google Drive API

#### 1.2 Configure OAuth Consent Screen
- [ ] Select "External" user type
- [ ] App name: "MTG Madness Carlo"
- [ ] User support email
- [ ] Developer contact email
- [ ] Add scopes:
  - openid
  - email
  - profile
  - spreadsheets
  - drive.file
- [ ] Add test users (during development)

#### 1.3 Create OAuth 2.0 Credentials
- [ ] Create "OAuth client ID"
- [ ] Application type: "Web application"
- [ ] Authorized JavaScript origins:
  - http://localhost:5173 (dev)
  - https://yourdomain.com (prod)
- [ ] Authorized redirect URIs:
  - http://localhost:8000/api/auth/google/callback (dev)
  - https://api.yourdomain.com/api/auth/google/callback (prod)
- [ ] Save Client ID and Client Secret

#### 1.4 Environment Variables
```env
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

---

## 📦 Phase 2: Backend Implementation

### Dependencies to Add

```python
# backend/requirements.txt
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.108.0
oauthlib==3.2.2
```

### 2.1 Update Database Schema

#### New Fields in `users` Table
```python
# backend/app/models/user.py
class User(Base):
    # Existing fields...
    
    # Google OAuth fields
    google_id = Column(String, unique=True, nullable=True, index=True)
    google_refresh_token = Column(String, nullable=True)  # Encrypted
    google_access_token = Column(String, nullable=True)   # Encrypted
    google_token_expiry = Column(DateTime, nullable=True)
    
    # Profile info from Google
    google_profile_picture = Column(String, nullable=True)
```

#### Migration
```bash
alembic revision -m "add_google_oauth_fields"
alembic upgrade head
```

### 2.2 Google OAuth Service

**File**: `backend/app/services/google_oauth.py`

```python
"""
Google OAuth Service

Handles OAuth flow and token management.
"""

from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleOAuthService:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL."""
        
    def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token."""
        
    def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh an expired access token."""
        
    def get_user_info(self, access_token: str) -> dict:
        """Get user profile from Google."""
```

### 2.3 Google Sheets Service

**File**: `backend/app/services/google_sheets.py`

```python
"""
Google Sheets Service

Creates and formats spreadsheets with simulation data.
"""

class GoogleSheetsExporter:
    def __init__(self, credentials):
        self.credentials = credentials
        self.sheets_service = build('sheets', 'v4', credentials=credentials)
        self.drive_service = build('drive', 'v3', credentials=credentials)
        
    def create_simulation_spreadsheet(
        self, 
        simulation_data: dict,
        title: str
    ) -> str:
        """
        Create a formatted spreadsheet with simulation results.
        
        Returns:
            URL of the created spreadsheet
        """
        
    def _create_summary_sheet(self, spreadsheet_id, data):
        """Create summary sheet with key statistics."""
        
    def _create_card_stats_sheet(self, spreadsheet_id, data):
        """Create card statistics sheet."""
        
    def _create_mulligan_sheet(self, spreadsheet_id, data):
        """Create mulligan analysis sheet."""
        
    def _create_charts(self, spreadsheet_id):
        """Add charts to visualize data."""
        
    def _format_spreadsheet(self, spreadsheet_id):
        """Apply formatting (colors, borders, fonts)."""
```

### 2.4 OAuth API Endpoints

**File**: `backend/app/api/google_auth.py`

```python
"""
Google OAuth API Endpoints
"""

@router.get("/auth/google/login")
def google_login(request: Request):
    """Initiate Google OAuth flow."""
    # Generate authorization URL
    # Redirect user to Google consent screen
    
@router.get("/auth/google/callback")
def google_callback(code: str, state: str, db: Session):
    """Handle OAuth callback from Google."""
    # Exchange code for tokens
    # Get user info
    # Create/update user in database
    # Return JWT token for app
    
@router.post("/auth/google/refresh")
def refresh_google_token(current_user: User, db: Session):
    """Refresh Google access token for Sheets API."""
    # Check if token expired
    # Refresh if needed
    # Update in database
```

### 2.5 Sheets Export API Endpoint

**File**: `backend/app/api/simulations.py` (add to existing)

```python
@router.post("/{simulation_id}/export-to-sheets")
def export_simulation_to_sheets(
    simulation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export simulation results to Google Sheets.
    
    Returns:
        {
            "spreadsheet_id": "...",
            "spreadsheet_url": "https://docs.google.com/spreadsheets/d/...",
            "message": "Successfully exported to Google Sheets"
        }
    """
    # Verify user has Google OAuth connected
    # Get simulation data
    # Create credentials from user's tokens
    # Export to Sheets
    # Return spreadsheet URL
```

---

## 📦 Phase 3: Frontend Implementation

### Dependencies to Add

```json
// frontend/package.json
{
  "dependencies": {
    "@react-oauth/google": "^0.12.1"
  }
}
```

### 3.1 Google OAuth Context

**File**: `frontend/src/contexts/GoogleAuthContext.tsx`

```typescript
/**
 * Google OAuth Context
 * 
 * Manages Google sign-in state and Sheets export functionality.
 */

interface GoogleAuthContextType {
  isGoogleConnected: boolean;
  googleProfile: GoogleProfile | null;
  signInWithGoogle: () => void;
  signOutFromGoogle: () => void;
  exportToSheets: (simulationId: string) => Promise<string>;
}
```

### 3.2 Google Sign-In Button

**File**: `frontend/src/components/GoogleSignInButton.tsx`

```typescript
/**
 * Google Sign-In Button
 * 
 * Displays "Sign in with Google" button on login page.
 */

export function GoogleSignInButton() {
  const handleGoogleLogin = async (credentialResponse: any) => {
    // Send credential to backend
    // Receive JWT token
    // Store in localStorage
    // Redirect to dashboard
  };
  
  return (
    <GoogleLogin
      onSuccess={handleGoogleLogin}
      onError={() => console.error('Google login failed')}
    />
  );
}
```

### 3.3 Export to Sheets Button

**File**: `frontend/src/components/ExportToSheetsButton.tsx`

```typescript
/**
 * Export to Google Sheets Button
 * 
 * Displays on simulation results page.
 */

interface ExportToSheetsButtonProps {
  simulationId: string;
  simulationName: string;
}

export function ExportToSheetsButton({ 
  simulationId, 
  simulationName 
}: ExportToSheetsButtonProps) {
  const [exporting, setExporting] = useState(false);
  const [spreadsheetUrl, setSpreadsheetUrl] = useState<string | null>(null);
  
  const handleExport = async () => {
    // Call API endpoint
    // Show loading state
    // Display spreadsheet link when done
  };
  
  return (
    <div>
      {!spreadsheetUrl ? (
        <button onClick={handleExport} disabled={exporting}>
          {exporting ? 'Exporting...' : '📊 Export to Google Sheets'}
        </button>
      ) : (
        <a href={spreadsheetUrl} target="_blank">
          🔗 Open in Google Sheets
        </a>
      )}
    </div>
  );
}
```

### 3.4 Update SimulationResults Component

**File**: `frontend/src/components/SimulationResults.tsx`

```typescript
// Add export button to results page
<div className="flex justify-between items-center mb-6">
  <h2>Simulation Results</h2>
  <ExportToSheetsButton 
    simulationId={simulation.id}
    simulationName={simulation.deck_name}
  />
</div>
```

### 3.5 Update AuthForm Component

**File**: `frontend/src/components/AuthForm.tsx`

```typescript
// Add Google sign-in option
<div className="mt-4">
  <div className="relative">
    <div className="absolute inset-0 flex items-center">
      <div className="w-full border-t border-gray-300" />
    </div>
    <div className="relative flex justify-center text-sm">
      <span className="px-2 bg-white text-gray-500">Or continue with</span>
    </div>
  </div>
  
  <div className="mt-4">
    <GoogleSignInButton />
  </div>
</div>
```

---

## 📦 Phase 4: Security Considerations

### 4.1 Token Storage
- **Refresh tokens**: Encrypt in database using `cryptography` library
- **Access tokens**: Encrypted, short-lived (1 hour)
- **Never expose tokens** in API responses
- **HTTPS only** for OAuth redirects (production)

### 4.2 Token Encryption Service

**File**: `backend/app/utils/encryption.py`

```python
"""
Token Encryption Service

Encrypts/decrypts sensitive OAuth tokens.
"""

from cryptography.fernet import Fernet

class TokenEncryption:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())
        
    def encrypt(self, token: str) -> str:
        """Encrypt a token."""
        return self.cipher.encrypt(token.encode()).decode()
        
    def decrypt(self, encrypted_token: str) -> str:
        """Decrypt a token."""
        return self.cipher.decrypt(encrypted_token.encode()).decode()
```

### 4.3 Scope Validation
- Only request necessary scopes
- Check scope before API calls
- Handle scope denial gracefully
- Prompt for re-authorization if needed

### 4.4 Rate Limiting
- Implement rate limits for Sheets API calls
- Cache user credentials
- Batch operations where possible

---

## 📦 Phase 5: Spreadsheet Formatting

### 5.1 Sheet Structure

#### Tab 1: Summary
- Key statistics (win rate, average lands, etc.)
- Setup success rates
- Mulligan overview
- Color-coded cells (green = good, red = bad)

#### Tab 2: Card Statistics
- Card name
- Times drawn
- Times in opening hand
- Times played
- Average turn drawn
- Conditional formatting

#### Tab 3: Key Cards
- Key card tracking
- Access rates by turn
- Success metrics
- Charts

#### Tab 4: Mulligan Analysis
- Hand size distribution
- Mulligan reasons
- Success rates
- Pie chart

#### Tab 5: Graveyard Stats
- Card frequency in graveyard
- Turn distribution
- Madness/Flashback tracking

### 5.2 Formatting Features
- **Headers**: Bold, colored background
- **Borders**: Grid lines for readability
- **Number formats**: Percentages, decimals
- **Conditional formatting**: Color scales
- **Charts**: Bar charts, pie charts, line graphs
- **Freeze panes**: Keep headers visible

---

## 📦 Phase 6: Error Handling

### Common Errors & Solutions

#### Token Expired
```python
try:
    # Make Sheets API call
except HttpError as e:
    if e.resp.status == 401:
        # Refresh token
        # Retry operation
```

#### Quota Exceeded
```python
# Show user-friendly message
# Suggest retry later
# Log for monitoring
```

#### Permission Denied
```python
# Check if scopes granted
# Prompt for re-authorization
```

#### Network Errors
```python
# Retry with exponential backoff
# Fallback to XLSX download
```

---

## 📦 Phase 7: Testing

### 7.1 Unit Tests
- OAuth flow simulation
- Token encryption/decryption
- Sheets API mock calls
- Data formatting logic

### 7.2 Integration Tests
- End-to-end OAuth flow
- Spreadsheet creation
- Export with real data
- Error scenarios

### 7.3 Manual Testing Checklist
- [ ] Sign in with Google
- [ ] Connect existing account to Google
- [ ] Export simulation to Sheets
- [ ] Verify spreadsheet formatting
- [ ] Test with large datasets
- [ ] Test token refresh
- [ ] Test error handling

---

## 📋 Implementation Timeline

### Week 1: Setup & OAuth
- Day 1-2: Google Cloud setup, credentials
- Day 3-4: Backend OAuth implementation
- Day 5: Frontend Google login button

### Week 2: Sheets Integration
- Day 1-2: Sheets API service implementation
- Day 3: Export endpoint
- Day 4-5: Frontend export button

### Week 3: Formatting & Polish
- Day 1-2: Spreadsheet formatting
- Day 3: Charts and conditional formatting
- Day 4-5: Error handling

### Week 4: Testing & Documentation
- Day 1-2: Testing
- Day 3-4: Bug fixes
- Day 5: Documentation

---

## 🔄 Alternative: Simple Approach (Quick Win)

If full OAuth is too complex initially, consider:

### Phase A: Download XLSX (Current Behavior)
- Export results to XLSX file
- User downloads to their computer
- User manually uploads to Google Sheets

### Phase B: Google Sheets Link
- Generate public spreadsheet
- Use service account (no user OAuth)
- Share link with user
- Read-only access

### Phase C: Full OAuth (Future)
- Implement full OAuth flow
- Export to user's Google Drive
- Full edit permissions

---

## 📊 Data Mapping: Simulation → Sheets

### Summary Sheet
```python
{
    "A1": "MTG Madness Carlo - Simulation Results",
    "A3": "Deck Name", "B3": simulation.deck.name,
    "A4": "Date", "B4": simulation.completed_at,
    "A5": "Runs", "B5": simulation.runs,
    "A6": "Turns", "B6": simulation.turns,
    "A8": "Average Lands", "B8": results.average_lands_in_play,
    "A9": "Win Rate", "B9": f"{results.win_rate}%",
    # ... more fields
}
```

### Card Stats Sheet
```python
# Headers
["Card Name", "Times Drawn", "Opening Hand %", "Avg Turn Drawn", "Times Played"]

# Data rows
for card in results.card_stats:
    [card.name, card.times_drawn, card.opening_hand_pct, card.avg_turn, card.times_played]
```

---

## 🎯 Success Criteria

### Minimum Viable Product (MVP)
- ✅ User can sign in with Google
- ✅ Existing users can connect Google account
- ✅ "Export to Sheets" button visible on results page
- ✅ Clicking button creates formatted spreadsheet
- ✅ User receives clickable link to spreadsheet
- ✅ Spreadsheet contains all simulation data
- ✅ Basic formatting (headers, borders)

### Nice to Have
- Charts and graphs
- Conditional formatting
- Color-coded cells
- Multiple tabs
- Share permissions
- Export history

---

## 📚 Resources

### Google Documentation
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Sheets API v4](https://developers.google.com/sheets/api)
- [Python Quickstart](https://developers.google.com/sheets/api/quickstart/python)

### Libraries
- [google-auth](https://google-auth.readthedocs.io/)
- [google-api-python-client](https://github.com/googleapis/google-api-python-client)
- [@react-oauth/google](https://www.npmjs.com/package/@react-oauth/google)

---

## 🎉 Summary

This plan provides a comprehensive roadmap for adding:
1. **Google OAuth login** (alternative authentication)
2. **Google Sheets export** (one-click export from results page)
3. **Formatted spreadsheets** (professional-looking output)
4. **Secure token management** (encrypted storage)

The implementation is broken into manageable phases with clear tasks, dependencies, and success criteria.

**Estimated Development Time**: 2-4 weeks (depending on complexity level chosen)

**Next Step**: Choose between:
- **Option A**: Full OAuth implementation (complete feature)
- **Option B**: Service account approach (simpler, faster)
- **Option C**: Hybrid (start with service account, add OAuth later)

Ready to begin implementation! 🚀

