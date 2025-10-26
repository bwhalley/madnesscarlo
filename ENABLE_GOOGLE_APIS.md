# 🔧 Fix: Enable Google APIs

## The Issue

You're seeing this error:
```
<HttpError 403 "The caller does not have permission">
```

This means the **Google Sheets API** and **Google Drive API** are not enabled in your Google Cloud project.

---

## ✅ Quick Fix (2 minutes)

### Step 1: Enable Google Sheets API

1. **Go to**: https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=madness-carlo-local

2. Click the **"ENABLE"** button

3. Wait for confirmation (5-10 seconds)

### Step 2: Enable Google Drive API

1. **Go to**: https://console.cloud.google.com/apis/library/drive.googleapis.com?project=madness-carlo-local

2. Click the **"ENABLE"** button

3. Wait for confirmation (5-10 seconds)

---

## 🔍 Alternative: Enable via Cloud Shell

If the web console doesn't work, use these commands:

```bash
# Set your project
gcloud config set project madness-carlo-local

# Enable Google Sheets API
gcloud services enable sheets.googleapis.com

# Enable Google Drive API
gcloud services enable drive.googleapis.com

# Verify they're enabled
gcloud services list --enabled | grep -E "sheets|drive"
```

You should see:
```
drive.googleapis.com                     Google Drive API
sheets.googleapis.com                    Google Sheets API
```

---

## ⏱️ Wait Time

After enabling the APIs:
- **Wait 1-2 minutes** for the changes to propagate
- Then **try the export again**

---

## 🧪 Test After Enabling

1. Wait 1-2 minutes
2. Go back to your app: http://localhost:5173
3. Go to **📊 Simulations** tab
4. Click on a completed simulation
5. Click **"📊 Export to Google Sheets"**
6. **It should work now!** 🎉

---

## 🐛 Still Getting 403?

### Check Organization Policies

Some organizations block API usage. Check if there are policies:

```bash
# List organization policies
gcloud org-policies list --project=madness-carlo-local

# Check for API restrictions
gcloud org-policies describe constraints/serviceuser.services \
  --project=madness-carlo-local
```

If you see policies restricting APIs, you'll need to:
1. Contact your organization admin, OR
2. Create a new project without organizational restrictions

---

## ✅ Verification

After enabling, verify the APIs are active:

```bash
# Check if APIs are enabled
gcloud services list --enabled --project=madness-carlo-local | grep -E "sheets|drive"
```

Expected output:
```
drive.googleapis.com                     Google Drive API
sheets.googleapis.com                    Google Sheets API
```

---

## 📝 What These APIs Do

### Google Sheets API
- Creates new spreadsheets
- Writes data to sheets
- Formats cells (bold, colors, etc.)
- Creates multiple tabs

### Google Drive API  
- Manages file permissions
- Returns shareable links
- Allows spreadsheet sharing (future feature)

---

## 🎯 Next Steps

1. **Enable both APIs** (links above)
2. **Wait 1-2 minutes**
3. **Try export again**
4. **Enjoy your spreadsheet!** 📊

---

## 💡 Pro Tip

You can also enable these APIs from the main API Library:
1. Go to: https://console.cloud.google.com/apis/library?project=madness-carlo-local
2. Search for "Google Sheets API" → Enable
3. Search for "Google Drive API" → Enable

---

**Let me know once you've enabled the APIs and we'll test again!** 🚀

