#!/bin/bash
# Test webhook by simulating Meta sending a message

echo "Testing webhook with simulated message..."
echo ""

curl -X POST https://whatsapp-webhook-765745173795.us-central1.run.app/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{
      "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
      "changes": [{
        "value": {
          "messaging_product": "whatsapp",
          "metadata": {
            "display_phone_number": "15550123456",
            "phone_number_id": "458350900695183"
          },
          "contacts": [{
            "profile": {
              "name": "Test User"
            },
            "wa_id": "15550199999"
          }],
          "messages": [{
            "from": "15550199999",
            "id": "wamid.test123",
            "timestamp": "1234567890",
            "text": {
              "body": "Hello, this is a test message!"
            },
            "type": "text"
          }]
        },
        "field": "messages"
      }]
    }]
  }'

echo ""
echo ""
echo "Check your Cloud Run logs to see if the message was received!"
