# 🔧 Troubleshooting: Google Sheets 403 Permission Error

## Current Status

✅ Google Sheets API is enabled  
✅ Google Drive API is enabled  
✅ Service account exists: `sheets-exporter@madness-carlo-local.iam.gserviceaccount.com`  
❌ Getting 403 "The caller does not have permission"

---

## 🎯 Most Likely Cause: Organization Policy

Your Google Cloud project might be under an organization that restricts service account usage.

---

## ✅ Solution 1: Check for Organization Policies (RECOMMENDED)

Run these commands in Google Cloud Shell:

```bash
# Check if your project is under an organization
gcloud projects describe madness-carlo-local --format="value(parent)"

# If it shows an organization, check for restrictive policies
gcloud org-policies list --project=madness-carlo-local

# Check for service account restrictions
gcloud org-policies describe constraints/iam.allowedPolicyMemberDomains \
  --project=madness-carlo-local 2>&1

# Check for API restrictions  
gcloud resource-manager org-policies describe \
  serviceuser.services \
  --project=madness-carlo-local 2>&1
```

### If You See Restrictions

You have 3 options:

**Option A: Request Policy Exception** (if you have org admin)
Contact your organization admin to whitelist the Sheets/Drive APIs

**Option B: Create New Project Without Organization**
```bash
# Create a new project NOT under your organization
gcloud projects create madness-carlo-test-$(date +%s) --name="Madness Carlo Test"
# Then follow the setup guide again with the new project
```

**Option C: Use a Personal Google Account**
- Create a new project in a personal Gmail account (no organization restrictions)

---

## ✅ Solution 2: Grant IAM Permissions to Service Account

Even though the APIs are enabled, the service account needs explicit permissions:

```bash
PROJECT_ID="madness-carlo-local"
SERVICE_ACCOUNT="sheets-exporter@madness-carlo-local.iam.gserviceaccount.com"

# Grant basic viewer role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/viewer"

# Check what roles it currently has
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT" \
  --format="table(bindings.role)"
```

---

## ✅ Solution 3: Enable Domain-Wide Delegation (For Organization Accounts)

If your project is under a Google Workspace organization:

```bash
# Check if domain-wide delegation is needed
gcloud iam service-accounts describe \
  sheets-exporter@madness-carlo-local.iam.gserviceaccount.com

# Enable domain-wide delegation
gcloud iam service-accounts update \
  sheets-exporter@madness-carlo-local.iam.gserviceaccount.com \
  --project=madness-carlo-local
```

Then in Google Workspace Admin Console:
1. Go to: https://admin.google.com/ac/owl/domainwidedelegation
2. Add the client ID with these scopes:
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/drive.file`

---

## ✅ Solution 4: Verify Service Account Key is Valid

Test the credentials directly:

```bash
# In Cloud Shell, test the service account
gcloud auth activate-service-account \
  --key-file=/path/to/google-service-account.json

# Try to list projects (should work if credentials are valid)
gcloud projects list

# Switch back to your user account
gcloud config set account brian@brianwhalley.com
```

---

## ✅ Solution 5: Check for API Restrictions

Some organizations restrict which APIs can be used:

```bash
# Check if there are API restrictions
gcloud services list --available | grep -E "sheets|drive"

# Check if there are any denied policies
gcloud projects get-iam-policy madness-carlo-local \
  --flatten="bindings[].members" \
  --format="table(bindings.role,bindings.members)"
```

---

## 🔍 Detailed Diagnostics

Run this comprehensive check:

```bash
#!/bin/bash
PROJECT_ID="madness-carlo-local"
SERVICE_ACCOUNT="sheets-exporter@madness-carlo-local.iam.gserviceaccount.com"

echo "=== PROJECT INFO ==="
gcloud projects describe $PROJECT_ID

echo ""
echo "=== ENABLED SERVICES ==="
gcloud services list --enabled --project=$PROJECT_ID | grep -E "sheets|drive"

echo ""
echo "=== SERVICE ACCOUNT INFO ==="
gcloud iam service-accounts describe $SERVICE_ACCOUNT --project=$PROJECT_ID

echo ""
echo "=== SERVICE ACCOUNT IAM ROLES ==="
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT"

echo ""
echo "=== ORGANIZATION POLICIES ==="
gcloud org-policies list --project=$PROJECT_ID 2>&1 | head -20

echo ""
echo "=== SERVICE ACCOUNT KEYS ==="
gcloud iam service-accounts keys list \
  --iam-account=$SERVICE_ACCOUNT \
  --project=$PROJECT_ID
```

---

## 🎯 Quick Test: Try a Simple API Call

Let's test if the service account can actually use the Sheets API:

```bash
# Get an access token for the service account
ACCESS_TOKEN=$(gcloud auth print-access-token \
  --impersonate-service-account=sheets-exporter@madness-carlo-local.iam.gserviceaccount.com)

# Try to create a spreadsheet
curl -X POST \
  "https://sheets.googleapis.com/v4/spreadsheets" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "title": "Test Spreadsheet"
    }
  }'
```

### What to Look For:

**If it works:**
```json
{
  "spreadsheetId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "properties": {
    "title": "Test Spreadsheet"
  }
}
```

**If it fails:**
```json
{
  "error": {
    "code": 403,
    "message": "The caller does not have permission"
  }
}
```

This will tell us if it's a service account permissions issue or an organization policy issue.

---

## 🚨 Common Causes & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| 403 "No permission" | Organization policy | Create project in personal account |
| 403 "No permission" | Service account needs IAM role | Grant `roles/viewer` |
| 403 "No permission" | Domain restriction | Enable domain-wide delegation |
| 403 "API not enabled" | APIs disabled | Already done ✅ |
| 403 "Service account disabled" | Account disabled | Re-enable service account |

---

## 🎯 Recommended Next Steps

1. **Check for organization** (most likely issue):
   ```bash
   gcloud projects describe madness-carlo-local --format="value(parent)"
   ```
   
   If it shows an organization, that's probably the blocker.

2. **Grant IAM permissions**:
   ```bash
   gcloud projects add-iam-policy-binding madness-carlo-local \
     --member="serviceAccount:sheets-exporter@madness-carlo-local.iam.gserviceaccount.com" \
     --role="roles/viewer"
   ```

3. **Test with the curl command above**

4. **If still failing**, you'll need to either:
   - Request organization policy exception
   - Create a new project in a personal Google account
   - Switch to OAuth flow (more complex, but no org restrictions)

---

## 🔄 Alternative: Create New Project in Personal Account

If organization policies are blocking you:

```bash
# Create new project with a random suffix
NEW_PROJECT="madness-carlo-$(date +%s)"

# Create the project (make sure you're using a PERSONAL Gmail account, not work)
gcloud projects create $NEW_PROJECT --name="Madness Carlo"

# Enable billing (required for APIs)
# You'll need to do this in the console: https://console.cloud.google.com/billing

# Enable APIs
gcloud services enable sheets.googleapis.com --project=$NEW_PROJECT
gcloud services enable drive.googleapis.com --project=$NEW_PROJECT

# Create new service account
gcloud iam service-accounts create sheets-exporter \
  --display-name="Sheets Exporter" \
  --project=$NEW_PROJECT

# Grant basic permissions
gcloud projects add-iam-policy-binding $NEW_PROJECT \
  --member="serviceAccount:sheets-exporter@${NEW_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/viewer"

# Create new key
gcloud iam service-accounts keys create new-google-service-account.json \
  --iam-account=sheets-exporter@${NEW_PROJECT}.iam.gserviceaccount.com \
  --project=$NEW_PROJECT

echo "✅ New service account key created: new-google-service-account.json"
echo "📋 Replace backend/google-service-account.json with this new file"
echo "🔄 Then restart: docker-compose restart backend celery-worker"
```

---

## 📞 Need Help?

Run the comprehensive diagnostics above and share the output. That will tell us exactly what's blocking the service account.

---

**Let's start with the organization check - that's the most likely culprit!** 🎯

