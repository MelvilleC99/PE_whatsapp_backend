# 🚀 Quick Start Guide

## ✅ All Files Created!

Your WhatsApp backend is ready. Here's what we built:

### 📂 Project Structure
```
PE_whatsapp_backend/
├── src/
│   ├── __init__.py              ✅ 20 lines
│   ├── config.py                ✅ 97 lines  - Configuration management
│   ├── utils.py                 ✅ 124 lines - Helper functions
│   ├── firebase_manager.py      ✅ 184 lines - Firebase operations
│   ├── whatsapp_sender.py       ✅ 206 lines - Meta WhatsApp API
│   ├── insight_generator.py     ✅ 175 lines - Database insights
│   └── scheduler.py             ✅ 149 lines - Main orchestrator
├── .env.example                 ✅ Template
├── .gitignore                   ✅ Complete
├── requirements.txt             ✅ All dependencies
└── README.md                    ✅ Full documentation

Total: ~955 lines of production-ready Python code
```

## 🎯 Setup Steps

### 1. Create Virtual Environment
```bash
cd /Users/melville/Documents/PE_whatsapp_backend
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 4. Get Your Meta Credentials

You need these from Meta Business Manager:
- ✅ **Access Token** (you have this - temporary token)
- ✅ **Business Account ID** (you have this)
- ❓ **Phone Number ID** (IMPORTANT - different from Business Account ID!)

**How to get Phone Number ID:**
1. Go to https://developers.facebook.com
2. Select your WhatsApp app
3. Click "WhatsApp" → "API Setup"
4. Find "Phone number ID" (looks like: `123456789012345`)
5. Copy this to your `.env` file

### 5. Test Everything

```bash
# Test configuration loading
python -m src.config

# Test Firebase connection
python -m src.firebase_manager

# Test WhatsApp API
python -m src.whatsapp_sender

# Test insight generator (with mock data)
python -m src.insight_generator
```

## 🏃‍♂️ Running the System

### Add Test User to Firebase
```python
from src.firebase_manager import FirebaseManager

fm = FirebaseManager()
fm.add_user(
    phone="27821234567",  # Your WhatsApp number
    name="Test User",
    frequency="weekly"
)
```

### Send Test Insights
```bash
# Run once with mock data (no database required)
python -m src.scheduler --once --mock

# Run once with real database
python -m src.scheduler --once

# Start scheduled job (every Monday at 9 AM)
python -m src.scheduler
```

## 📱 What Gets Sent

Users will receive:
```
📊 *Weekly Property Insights for John Doe*

📈 Sales: +5%
🏠 Active Listings: 45
💰 Avg Price: R450K
⚡ Sales Velocity: 12 days

_Generated on 13 November 2025_
```

## 🔥 Firebase Setup

1. Go to Firebase Console: https://console.firebase.google.com
2. Select your project
3. Go to Project Settings → Service Accounts
4. Click "Generate new private key"
5. Extract these values to `.env`:
   - `firebase_project_id`
   - `firebase_private_key_id`
   - `firebase_private_key`
   - `firebase_client_email`
   - `firebase_client_id`

## 🎨 Features Built-In

✅ **Send text messages** - Plain text with formatting
✅ **Interactive buttons** - Up to 3 reply buttons
✅ **List messages** - Dropdown lists for options
✅ **Firebase user management** - Add/remove users
✅ **Automatic scheduling** - Weekly insights
✅ **Mock data mode** - Test without database
✅ **Error handling** - Robust logging
✅ **Phone formatting** - Automatic E.164 conversion

## 🐛 Troubleshooting

**"Invalid OAuth access token"**
→ Your temporary token expired (24hr limit). Generate new one from Meta.

**"Phone number not found"**  
→ Using Business Account ID instead of Phone Number ID. Get the Phone Number ID from API Setup.

**"Firebase connection failed"**
→ Check your service account credentials in `.env`

**Database connection issues**
→ Use `--mock` flag to test without database first

## 🚀 Next Steps

1. ✅ Setup `.env` with real credentials
2. ✅ Test WhatsApp connection: `python -m src.whatsapp_sender`
3. ✅ Add yourself as test user in Firebase
4. ✅ Send test insight: `python -m src.scheduler --once --mock`
5. ✅ Customize database queries in `insight_generator.py`
6. ✅ Deploy to production (Cloud Run, Heroku, Railway)

## 💡 Pro Tips

- **Start with mock data** - Test the flow before connecting real database
- **Test with your own number** - Add yourself as first user
- **Check logs** - All errors are logged to `logs/whatsapp_backend.log`
- **Rate limiting** - Code includes 1 second delay between messages
- **Permanent tokens** - Convert temporary token to permanent in Meta settings

---

**Ready to test?** Run: `python -m src.whatsapp_sender`

This will verify your Meta credentials work! 🎉
