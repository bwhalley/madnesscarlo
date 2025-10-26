# Google Sheets Service Account Setup Guide

## 🎯 Quick Setup (10 minutes)

Follow these steps to enable Google Sheets export functionality.

---

## Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project**
   - Click "Select a project" dropdown at the top
   - Click "New Project"
   - **Project Name**: `mtg-madness-carlo`
   - Click "Create"
   - Wait for project creation (~30 seconds)

---

## Step 2: Enable Google Sheets API

1. **Navigate to APIs & Services**
   - In the left sidebar: "APIs & Services" → "Library"
   - Or visit: https://console.cloud.google.com/apis/library

2. **Enable Google Sheets API**
   - Search for "Google Sheets API"
   - Click on "Google Sheets API"
   - Click "Enable"
   - Wait for enablement (~10 seconds)

3. **Enable Google Drive API** (for sharing)
   - Search for "Google Drive API"
   - Click on "Google Drive API"  
   - Click "Enable"
   - Wait for enablement (~10 seconds)

---

## Step 3: Create Service Account

1. **Navigate to Credentials**
   - Left sidebar: "APIs & Services" → "Credentials"
   - Or visit: https://console.cloud.google.com/apis/credentials

2. **Create Service Account**
   - Click "+ CREATE CREDENTIALS" at the top
   - Select "Service Account"

3. **Service Account Details**
   - **Service account name**: `sheets-exporter`
   - **Service account ID**: `sheets-exporter` (auto-filled)
   - **Description**: `Service account for exporting simulation results to Google Sheets`
   - Click "Create and Continue"

4. **Grant Permissions** (Optional)
   - Click "Continue" (no roles needed for basic usage)

5. **Done**
   - Click "Done"

---

## Step 4: Create Service Account Key

1. **Find Your Service Account**
   - On the Credentials page, scroll to "Service Accounts"
   - Click on the `sheets-exporter@...` email

2. **Create Key**
   - Click the "Keys" tab
   - Click "Add Key" → "Create new key"
   - Select "JSON" format
   - Click "Create"

3. **Save the Key File**
   - A JSON file will download automatically
   - **Filename**: `mtg-madness-carlo-xxxxx.json`
   - ⚠️ **Important**: Keep this file secure! It's like a password.

4. **Rename the File**
   - Rename to: `google-service-account.json`
   - Move to: `/Users/brian/madnesscarlo/backend/`

---

## Step 5: Configure Environment

### Option A: Docker (Recommended for Development)

1. **Update docker-compose.yml**

```yaml
backend:
  # ... existing config ...
  environment:
    # ... existing vars ...
    - GOOGLE_SERVICE_ACCOUNT_FILE=/app/google-service-account.json
  volumes:
    - ./backend:/app
    - /app/venv
    # Add this line:
    - ./backend/google-service-account.json:/app/google-service-account.json:ro
```

### Option B: Direct Environment Variable

1. **Set environment variable**

```bash
export GOOGLE_SERVICE_ACCOUNT_FILE=/Users/brian/madnesscarlo/backend/google-service-account.json
```

2. **Add to .env file** (optional)

```bash
# backend/.env
GOOGLE_SERVICE_ACCOUNT_FILE=/app/google-service-account.json
```

---

## Step 6: Secure the Credentials

1. **Add to .gitignore**

```bash
# Add to .gitignore
backend/google-service-account.json
google-service-account.json
*-service-account.json
```

2. **Verify it's ignored**

```bash
cd /Users/brian/madnesscarlo
git status
# Should NOT show google-service-account.json
```

---

## Step 7: Test the Setup

Once the backend is updated and restarted:

```bash
# Rebuild backend with new dependencies
docker-compose build backend

# Restart services
docker-compose restart backend celery-worker

# Check logs for errors
docker-compose logs backend | grep -i "google\|sheets\|service"
```

---

## 🔍 Verify Setup

### Check Service Account Email

Your service account email looks like:
```
sheets-exporter@mtg-madness-carlo.iam.gserviceaccount.com
```

This email is what will "own" the exported spreadsheets.

### Test Export

1. Run a simulation in the app
2. Click "Export to Google Sheets"
3. Check that a spreadsheet is created
4. Verify you can open it

---

## 📊 How It Works

```
App creates spreadsheet using service account
    ↓
Spreadsheet owned by: sheets-exporter@...
    ↓
App can set sharing permissions:
    - Anyone with link (view)
    - Anyone with link (edit)
    - Specific email addresses
    ↓
User receives link to spreadsheet
```

---

## 🔐 Security Best Practices

### 1. Protect the JSON Key File
- ✅ Never commit to git
- ✅ Never share publicly
- ✅ Limit access to production servers
- ✅ Rotate keys periodically

### 2. Set Appropriate Permissions
- Only enable APIs you need
- Don't grant unnecessary roles
- Review service account usage

### 3. Monitor Usage
- Check Google Cloud Console for API usage
- Set up billing alerts (free tier is generous)
- Review created spreadsheets periodically

---

## 💰 Cost & Limits

### Free Tier Limits (More Than Enough!)
- **API Calls**: 
  - Reads: 10 million per day
  - Writes: 500 per 100 seconds per user
- **Storage**: 15 GB (for service account)
- **Spreadsheets**: Unlimited (within storage)

### Typical Usage
- Export 1 simulation: ~10-20 API calls
- Storage per sheet: ~100-500 KB
- **You can export thousands of simulations for free!**

---

## 🐛 Troubleshooting

### Error: "Service account key file not found"
```bash
# Check file exists
ls -la /Users/brian/madnesscarlo/backend/google-service-account.json

# Check docker volume mount
docker-compose config | grep google-service-account
```

### Error: "API not enabled"
- Go back to Step 2
- Enable Google Sheets API
- Enable Google Drive API
- Wait 1-2 minutes for propagation

### Error: "Permission denied"
```bash
# Check file permissions
chmod 600 /Users/brian/madnesscarlo/backend/google-service-account.json

# Check docker can read it
docker-compose exec backend ls -la /app/google-service-account.json
```

### Error: "Invalid credentials"
- Re-download the JSON key
- Make sure it's not corrupted
- Check it's valid JSON: `cat backend/google-service-account.json | python -m json.tool`

---

## 📝 File Structure

```
madnesscarlo/
├── backend/
│   ├── google-service-account.json  ← Your credentials (git-ignored)
│   ├── app/
│   │   ├── services/
│   │   │   └── google_sheets.py     ← Sheets service
│   │   └── api/
│   │       └── simulations.py       ← Export endpoint
│   └── requirements.txt             ← Google libraries
├── .gitignore                       ← Ignore credentials
└── docker-compose.yml               ← Volume mount
```

---

## ✅ Checklist

Before running the app:

- [ ] Google Cloud project created
- [ ] Google Sheets API enabled
- [ ] Google Drive API enabled
- [ ] Service account created
- [ ] JSON key downloaded
- [ ] Key file in `backend/google-service-account.json`
- [ ] File added to .gitignore
- [ ] Environment variable set (or docker-compose updated)
- [ ] Backend rebuilt with new dependencies
- [ ] Services restarted

---

## 🎉 You're Done!

Once these steps are complete, you can:
1. ✅ Export simulations to Google Sheets
2. ✅ View formatted spreadsheets
3. ✅ Share links with others
4. ✅ Keep all data organized

**Next**: Start the backend and try exporting a simulation! 🚀

---

## 📚 Additional Resources

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Service Account Guide](https://cloud.google.com/iam/docs/service-accounts)
- [Python Client Library](https://github.com/googleapis/google-api-python-client)

---

## 💡 Pro Tips

### Tip 1: Share with Yourself
Add your email to get spreadsheets in your Drive:
```python
# In the export service
sheet.share(
    email_address="your@email.com",
    perm_type="user",
    role="writer"
)
```

### Tip 2: Organize in Folder
Create a folder for all exports:
```python
# Create folder once
folder_id = drive.create_folder("MTG Simulations")

# Put new sheets in folder
sheet.move_to_folder(folder_id)
```

### Tip 3: Set Expiration
Auto-delete old sheets after 30 days:
```python
# Set file expiration
expiration_date = datetime.now() + timedelta(days=30)
sheet.set_expiration(expiration_date)
```

---

**Ready to implement!** Let me know when your service account is set up, and I'll help with any issues. 🎯

