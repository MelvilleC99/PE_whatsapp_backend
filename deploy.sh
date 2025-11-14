#!/bin/bash
# Deploy WhatsApp Webhook to Google Cloud Run
# Project: proptech-email-management

set -e

echo "========================================"
echo "Deploying WhatsApp Webhook to Cloud Run"
echo "Project: proptech-email-management"
echo "========================================"
echo

# Load environment variables
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    exit 1
fi

source .env

# Set project
gcloud config set project proptech-email-management

echo "Building and deploying..."
echo

# Deploy to Cloud Run with environment variables
gcloud run deploy whatsapp-webhook \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --timeout 300 \
  --set-env-vars "WHATSAPP_ACCESS_TOKEN=${WHATSAPP_ACCESS_TOKEN},WHATSAPP_PHONE_NUMBER_ID=${WHATSAPP_PHONE_NUMBER_ID},WHATSAPP_BUSINESS_ACCOUNT_ID=${WHATSAPP_BUSINESS_ACCOUNT_ID},META_APP_ID=${META_APP_ID},META_APP_SECRET=${META_APP_SECRET},FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID},FIREBASE_CLIENT_EMAIL=${FIREBASE_CLIENT_EMAIL},FIREBASE_PRIVATE_KEY=${FIREBASE_PRIVATE_KEY},WEBHOOK_VERIFY_TOKEN=${WEBHOOK_VERIFY_TOKEN},DATABASE_HOST=${DATABASE_HOST},DATABASE_PORT=${DATABASE_PORT},DATABASE_NAME=${DATABASE_NAME},DATABASE_USER=${DATABASE_USER},DATABASE_PASSWORD=${DATABASE_PASSWORD},ENVIRONMENT=production,LOG_LEVEL=INFO,TIMEZONE=Africa/Johannesburg"

echo
echo "========================================"
echo "✅ Deployment complete!"
echo "========================================"
echo
echo "Your webhook URL:"
echo "https://whatsapp-webhook-765745173795.us-central1.run.app/webhook"
echo
echo "Verify Token: mySecretToken123"
echo
echo "Testing webhook..."
curl -s "https://whatsapp-webhook-765745173795.us-central1.run.app/webhook?hub.mode=subscribe&hub.verify_token=mySecretToken123&hub.challenge=test123"
echo
echo
