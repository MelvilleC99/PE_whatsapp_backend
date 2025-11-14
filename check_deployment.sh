#!/bin/bash
# Check deployment status

echo "Checking Cloud Run service status..."
echo

gcloud run services describe whatsapp-webhook \
  --region us-central1 \
  --project proptech-whatsapp \
  --format="value(status.url,status.conditions)"

echo
echo "Checking recent logs..."
echo

gcloud logs read \
  --limit 20 \
  --project proptech-whatsapp \
  --resource-type cloud_run_revision \
  --format="value(timestamp,textPayload,jsonPayload.message)"
