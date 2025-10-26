# Phase 3: Production & Integration Features

## Overview

Phase 3 focuses on production deployment readiness and external integrations to enhance the application's usability and accessibility.

---

## 🔒 1. SSL/TLS via Let's Encrypt

### Goal
Enable HTTPS for secure production deployment using Let's Encrypt free SSL certificates.

### Implementation Plan

#### Components Needed
- **Nginx** - Reverse proxy and SSL termination
- **Certbot** - Let's Encrypt certificate management
- **Docker Compose updates** - Add nginx service

#### Files to Create/Modify

**1. `nginx.conf`**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Backend API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Frontend
    location / {
        proxy_pass http://frontend:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**2. Update `docker-compose.yml`**
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - backend
      - frontend
    networks:
      - madness-network

  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

**3. Certificate Setup Script** - `setup-ssl.sh`
```bash
#!/bin/bash
# Initial certificate setup
docker-compose run --rm certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your@email.com \
  --agree-tos \
  --no-eff-email
```

#### Security Enhancements
- Force HTTPS redirect
- HSTS headers
- Secure cookie flags
- CORS updates for HTTPS
- CSP headers

#### Testing Checklist
- ✅ Certificate obtained successfully
- ✅ HTTPS loads correctly
- ✅ HTTP redirects to HTTPS
- ✅ Certificate auto-renewal works
- ✅ API endpoints accessible via HTTPS
- ✅ Frontend loads securely
- ✅ WebSocket connections work (if implemented)

#### Configuration Updates Needed
- Update `CORS_ORIGINS` in backend config
- Update frontend API base URL
- Set secure cookie flags
- Update OAuth redirect URIs (when implementing Google OAuth)

---

## 📊 2. Google Sheets Integration

### Goal
Export simulation results directly to Google Sheets for easy sharing, analysis, and record-keeping.

### Implementation Plan

#### Features
- **Export Results** - Send simulation data to a new or existing Google Sheet
- **Automatic Formatting** - Create formatted sheets with tables and charts
- **Share Access** - Automatically share sheet with user
- **Multiple Exports** - Support for different data views (summary, detailed, comparison)

#### Architecture

**Backend Components:**
1. **Google Sheets API Client** - Authentication and API calls
2. **Export Service** - Format and send data
3. **API Endpoints** - Trigger exports

**Frontend Components:**
1. **Export Button** - On simulation results page
2. **Export Options Modal** - Choose what to export
3. **Success/Progress Feedback** - Show export status

#### Files to Create

**1. Backend - Google Sheets Service** - `backend/app/services/google_sheets.py`
```python
"""
Google Sheets Export Service
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import Dict, List, Any

class GoogleSheetsService:
    def __init__(self, credentials: Credentials):
        self.service = build('sheets', 'v4', credentials=credentials)
    
    def create_simulation_sheet(
        self,
        simulation_data: Dict[str, Any],
        title: str
    ) -> str:
        """
        Create a new Google Sheet with simulation results.
        Returns the sheet URL.
        """
        # Create spreadsheet
        spreadsheet = {
            'properties': {'title': title},
            'sheets': [
                {'properties': {'title': 'Summary'}},
                {'properties': {'title': 'Card Stats'}},
                {'properties': {'title': 'Key Cards'}},
                {'properties': {'title': 'Ideal Setups'}},
                {'properties': {'title': 'Mulligan Stats'}}
            ]
        }
        
        result = self.service.spreadsheets().create(
            body=spreadsheet
        ).execute()
        
        spreadsheet_id = result['spreadsheetId']
        
        # Populate sheets
        self._populate_summary(spreadsheet_id, simulation_data)
        self._populate_card_stats(spreadsheet_id, simulation_data)
        self._populate_key_cards(spreadsheet_id, simulation_data)
        # ... more sheets
        
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
```

**2. Backend - API Endpoint** - `backend/app/api/exports.py`
```python
"""
Export API Endpoints
"""
from fastapi import APIRouter, Depends
from app.services.google_sheets import GoogleSheetsService

router = APIRouter(prefix="/api/exports", tags=["exports"])

@router.post("/simulations/{simulation_id}/google-sheets")
async def export_to_google_sheets(
    simulation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export simulation results to Google Sheets"""
    # Get simulation
    simulation = get_simulation_or_404(simulation_id, current_user, db)
    
    # Get user's Google credentials
    credentials = get_user_google_credentials(current_user)
    
    # Export to Google Sheets
    sheets_service = GoogleSheetsService(credentials)
    sheet_url = sheets_service.create_simulation_sheet(
        simulation.results,
        title=f"Simulation Results - {simulation.deck.name}"
    )
    
    return {
        "sheet_url": sheet_url,
        "message": "Successfully exported to Google Sheets"
    }
```

**3. Frontend - Export Component** - `frontend/src/components/ExportToSheets.tsx`
```typescript
export function ExportToSheets({ simulationId }: Props) {
  const [exporting, setExporting] = useState(false);
  
  const handleExport = async () => {
    setExporting(true);
    try {
      const response = await api.post(
        `/api/exports/simulations/${simulationId}/google-sheets`
      );
      
      // Open the sheet in new tab
      window.open(response.data.sheet_url, '_blank');
      
      toast.success('Exported to Google Sheets!');
    } catch (error) {
      toast.error('Failed to export');
    } finally {
      setExporting(false);
    }
  };
  
  return (
    <button onClick={handleExport} disabled={exporting}>
      {exporting ? 'Exporting...' : 'Export to Google Sheets'}
    </button>
  );
}
```

#### Google API Setup

**Prerequisites:**
1. Create Google Cloud Project
2. Enable Google Sheets API
3. Create OAuth 2.0 credentials
4. Add authorized redirect URIs

**Environment Variables:**
```bash
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/google/callback
```

**User Flow:**
1. User clicks "Export to Google Sheets"
2. If not connected, redirect to Google OAuth
3. User grants permission to create/edit sheets
4. Store OAuth tokens in database
5. Create sheet with simulation data
6. Return sheet URL to user

#### Data Export Format

**Sheet 1: Summary**
```
Simulation Summary
═══════════════════════════════════════════════
Deck Name:              My Madness Deck
Simulations Run:        10,000
Turns Simulated:        4
Date:                   2025-10-26

Key Metrics
───────────────────────────────────────────────
Avg Lands in Play:      3.2
Avg Cards Seen:         11.4
Avg Mulligans:          0.8
0 Mulligan %:           45.2%
```

**Sheet 2: Card Stats**
```
Card Name          | Seen % | Cast % | In Graveyard % |
──────────────────────────────────────────────────────
Survival of Fittest| 78.5   | 65.2   | 45.3          |
Careful Study      | 85.2   | 72.1   | 68.9          |
Basking Rootwalla  | 92.3   | 15.6   | 12.4          |
```

**Sheet 3: Key Cards** (similar format)

**Sheet 4: Ideal Setups**
```
Setup Name              | Success % | Avg Turn |
────────────────────────────────────────────────
Turn 2 Survival + Squee | 45.2      | 2.1      |
Turn 3 Engine Online    | 68.5      | 2.8      |
```

#### Requirements to Add
```txt
# Backend
google-auth==2.23.0
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.100.0
```

```json
// Frontend
{
  "react-google-login": "^5.2.2"
}
```

#### Features to Implement
- ✅ OAuth 2.0 flow for Google
- ✅ Token storage and refresh
- ✅ Create new spreadsheet
- ✅ Format data into sheets
- ✅ Add charts (optional)
- ✅ Share sheet with user
- ✅ Export multiple simulations at once
- ✅ Export comparison results

#### Testing Checklist
- ✅ Google OAuth flow works
- ✅ Tokens stored securely
- ✅ Sheet created successfully
- ✅ Data formatted correctly
- ✅ All sheets populated
- ✅ Charts render (if implemented)
- ✅ User can access sheet
- ✅ Error handling for API failures

---

## 📋 Phase 3 Task Breakdown

### Task 1: SSL Implementation (4-6 hours)
1. Create nginx configuration
2. Update docker-compose.yml
3. Create SSL setup script
4. Test certificate acquisition
5. Configure auto-renewal
6. Update security headers
7. Test HTTPS enforcement

### Task 2: Google Sheets Integration (8-10 hours)
1. Set up Google Cloud Project
2. Configure OAuth 2.0
3. Implement Google OAuth flow in backend
4. Create Google Sheets service
5. Add export API endpoints
6. Create frontend export component
7. Implement data formatting
8. Add export progress feedback
9. Test full export flow
10. Handle edge cases and errors

---

## 🚀 Deployment Considerations

### SSL/TLS
- **Domain Required** - Need a domain name for Let's Encrypt
- **DNS Configuration** - Point domain to server
- **Firewall Rules** - Open ports 80 and 443
- **Certificate Renewal** - Automated via Certbot
- **Monitoring** - Alert on cert expiration

### Google Sheets
- **Rate Limits** - Google Sheets API has quotas
- **Token Management** - Refresh tokens before expiration
- **Error Handling** - Graceful failures
- **User Privacy** - Clear data access policies
- **Scope Minimization** - Request only needed permissions

---

## 📊 Success Metrics

### SSL
- ✅ A+ rating on SSL Labs
- ✅ All traffic encrypted
- ✅ Auto-renewal working
- ✅ No cert warnings

### Google Sheets
- ✅ Export success rate > 99%
- ✅ Export time < 5 seconds
- ✅ User satisfaction with format
- ✅ Sheets are shareable

---

## 🔮 Future Enhancements (Phase 4+)

### Additional Integrations
- **Google Drive** - Save results to user's Drive
- **Excel Export** - Download as .xlsx
- **PDF Reports** - Generate PDF summaries
- **Email Reports** - Email results after simulation
- **Slack/Discord** - Notifications on completion

### Advanced SSL Features
- **Certificate Pinning** - Mobile app security
- **OCSP Stapling** - Faster cert validation
- **CAA Records** - DNS-based CA authorization
- **Certificate Transparency** - Monitor for misuse

### Analytics & Monitoring
- **Application Performance Monitoring** - Track response times
- **Error Tracking** - Sentry integration
- **Usage Analytics** - Track feature adoption
- **Cost Monitoring** - API usage and costs

---

## 📝 Documentation Needs

### For Users
- How to export to Google Sheets
- Setting up Google account connection
- Understanding SSL/HTTPS security
- Troubleshooting export issues

### For Developers
- SSL certificate setup guide
- Google API configuration
- Nginx configuration reference
- Production deployment checklist

---

## ⚡ Quick Reference

### SSL Setup Commands
```bash
# Initial setup
./setup-ssl.sh

# Renew certificate manually
docker-compose run --rm certbot renew

# Check certificate expiration
docker-compose run --rm certbot certificates

# Test nginx config
docker-compose exec nginx nginx -t
```

### Google Sheets API
```python
# Create sheet
sheet_url = sheets_service.create_simulation_sheet(data, title)

# Update sheet
sheets_service.update_range(sheet_id, range, values)

# Share sheet
sheets_service.share_with_user(sheet_id, user_email)
```

---

## 🎯 Phase 3 Goals

**Primary Goals:**
1. ✅ Secure production deployment with SSL
2. ✅ Easy data export via Google Sheets

**Secondary Goals:**
- Improved user experience
- Better data accessibility
- Production-ready infrastructure

**Success Criteria:**
- HTTPS working on production domain
- Users can export simulation results to Google Sheets
- No security warnings or issues
- Export process is smooth and reliable

---

## Timeline Estimate

- **SSL Implementation:** 1-2 days
- **Google Sheets Integration:** 2-3 days
- **Testing & Polish:** 1 day
- **Documentation:** 0.5 days

**Total Phase 3 Duration:** ~5-7 days

---

Ready to implement these features once Phase 2 is complete! 🚀

