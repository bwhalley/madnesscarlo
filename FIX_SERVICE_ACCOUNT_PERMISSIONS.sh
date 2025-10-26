#!/bin/bash
# Fix Service Account Permissions for Google Sheets Export

PROJECT_ID="madness-carlo-local"
SERVICE_ACCOUNT="sheets-exporter@madness-carlo-local.iam.gserviceaccount.com"

echo "🔍 Checking current IAM roles for service account..."
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT" \
  --format="table(bindings.role)"

echo ""
echo "✅ Granting necessary IAM roles..."

# Grant basic project viewer role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/viewer" \
  --condition=None

echo ""
echo "📊 Verifying roles were granted..."
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT" \
  --format="table(bindings.role)"

echo ""
echo "✅ Done! Service account now has necessary permissions."
echo ""
echo "⏱️  Wait 1-2 minutes for IAM changes to propagate, then try export again."

