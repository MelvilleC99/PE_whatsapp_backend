#!/bin/bash
# Quick script to update WhatsApp access token in Cloud Run
# Usage: ./update_token.sh YOUR_NEW_TOKEN

set -e

if [ -z "$1" ]; then
    echo "❌ Error: No token provided"
    echo ""
    echo "Usage: ./update_token.sh YOUR_NEW_TOKEN"
    echo ""
    echo "Example:"
    echo "  ./update_token.sh EAATfbYMdqIkBP1T7Hup1Kp..."
    exit 1
fi

NEW_TOKEN=$1

echo "=========================================="
echo "Updating WhatsApp Access Token"
echo "=========================================="
echo ""
echo "Service: whatsapp-webhook"
echo "Region: us-central1"
echo "Project: proptech-email-management"
echo ""
echo "New token: ${NEW_TOKEN:0:20}..." 
echo ""

# Update the token in Cloud Run
gcloud run services update whatsapp-webhook \
  --region us-central1 \
  --project proptech-email-management \
  --update-env-vars WHATSAPP_ACCESS_TOKEN=$NEW_TOKEN

echo ""
echo "=========================================="
echo "✅ Token updated successfully!"
echo "=========================================="
echo ""
echo "The service is redeploying with the new token."
echo "This usually takes 30-60 seconds."
echo ""
echo "Your webhook will automatically use the new token!"
