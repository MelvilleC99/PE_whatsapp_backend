#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "  PE WhatsApp Backend - Quick Test"
echo "════════════════════════════════════════════════════════════════"
echo ""

cd /Users/melville/Documents/PE_whatsapp_backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/installed" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
    touch venv/installed
    echo "✅ Dependencies installed"
    echo ""
fi

# Setup Melville's account
echo "👤 Setting up your user account..."
python setup_melville.py

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Ready to send WhatsApp message!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Run this command to send yourself a test message:"
echo "  python -m src.scheduler --once"
echo ""
echo "Or just run:"
echo "  ./send_test.sh"
echo ""
