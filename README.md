# PE WhatsApp Backend

WhatsApp automation system for sending property insights to customers via Meta's WhatsApp Business API.

## Features

- 📊 Automated insight generation from property CRM database
- 📱 WhatsApp message delivery via Meta Business API
- 🔥 Firebase user management
- ⏰ Scheduled weekly insights
- 🎯 Template-based messaging

## Project Structure

```
PE_whatsapp_backend/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management
│   ├── firebase_manager.py      # Firebase operations
│   ├── insight_generator.py     # Database queries & analysis
│   ├── whatsapp_sender.py       # Meta WhatsApp API
│   ├── scheduler.py             # Job orchestration
│   └── utils.py                 # Helper functions
├── .env                         # Environment variables (create from .env.example)
├── .env.example                 # Template for environment variables
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Setup

### 1. Clone and Navigate
```bash
cd /Users/melville/Documents/PE_whatsapp_backend
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

#### Required Variables:
- **WHATSAPP_ACCESS_TOKEN**: From Meta Business Manager
- **WHATSAPP_PHONE_NUMBER_ID**: Your WhatsApp Business phone number ID
- **WHATSAPP_BUSINESS_ACCOUNT_ID**: Your business account ID
- **Firebase credentials**: Download from Firebase Console
- **Database credentials**: Your property CRM database

### 5. Firebase Setup
1. Go to Firebase Console
2. Download service account JSON
3. Extract credentials to `.env` file

### 6. Test Meta API Connection
```bash
python -c "from src.whatsapp_sender import WhatsAppSender; sender = WhatsAppSender(); print('✅ Connection successful!' if sender.test_connection() else '❌ Connection failed')"
```

## Usage

### Manual Run
```bash
python -m src.scheduler
```

### Run Specific Components
```bash
# Test WhatsApp sending
python -m src.whatsapp_sender

# Generate insights
python -m src.insight_generator

# Test Firebase
python -m src.firebase_manager
```

## Meta WhatsApp API Setup

### Getting Your Credentials

1. **Go to Meta Business Manager**: https://business.facebook.com/
2. **Create/Select App**: Go to developers.facebook.com
3. **Add WhatsApp Product**: In your app dashboard
4. **Get Phone Number ID**:
   - Settings → WhatsApp → API Setup
   - Copy "Phone number ID"
5. **Get Access Token**:
   - Settings → WhatsApp → API Setup  
   - Copy temporary access token (valid 24 hours)
   - For production: Generate permanent token
6. **Get Business Account ID**:
   - Settings → WhatsApp → API Setup
   - Listed as "WhatsApp Business Account ID"

### No Webhook Needed for Sending
This project only SENDS messages, so you don't need to configure webhooks in Meta.

## Deployment Options

- **Local Cron**: Run on your server with cron jobs
- **Cloud Scheduler**: Google Cloud Scheduler + Cloud Functions
- **Heroku**: With Heroku Scheduler
- **Railway/Render**: With built-in cron
- **GitHub Actions**: Scheduled workflows

## Troubleshooting

### Common Issues

**"Invalid OAuth access token"**
- Token expired (temporary tokens last 24 hours)
- Generate new token from Meta Business Manager

**"Phone number not found"**
- Using Business Account ID instead of Phone Number ID
- Check Settings → WhatsApp → API Setup

**Firebase connection failed**
- Check Firebase credentials in .env
- Ensure service account has correct permissions

## License

Proprietary - Property Engine
