#!/bin/bash

cd /Users/melville/Documents/PE_whatsapp_backend

echo "════════════════════════════════════════════════════════════════"
echo "  Sending WhatsApp Test Message (from Firebase)"
echo "════════════════════════════════════════════════════════════════"
echo ""

source venv/bin/activate

# Send using insights already saved in Firebase (no database needed)
python send_from_firebase.py

echo ""
