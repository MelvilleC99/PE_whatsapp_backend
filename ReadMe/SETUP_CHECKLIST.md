# 🎯 WHAT YOU NEED - Simple Checklist

## ✅ What You Already Have:

```
✓ App Name: Property Engine Sudonum
✓ App ID: 451967794668922
✓ App Secret (Client Secret): [you have this]
✓ Temporary Access Token: [you have this]
✓ Business Account ID: [you have this]
```

## ❓ What You Still Need:

```
? Phone Number ID: [NEED TO FIND THIS]
```

---

## 🚀 3-Step Process to Get Started:

### Step 1: Find Your Phone Number ID
```bash
cd /Users/melville/Documents/PE_whatsapp_backend
python find_phone_number_id.py
```

**What to enter:**
- App ID: `451967794668922` (press Enter to use default)
- Access Token: [paste your temporary token]

**What you'll get:**
```
🆔 Phone Number ID: 123456789012345
```

### Step 2: Update .env File
Copy the output from Step 1 and paste into `.env`

Or manually edit:
```bash
nano .env
```

Add these lines:
```
WHATSAPP_ACCESS_TOKEN=your_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_BUSINESS_ACCOUNT_ID=451967794668922
```

### Step 3: Test It
```bash
python test_setup.py
```

If you see all ✅ checks, you're done!

---

## 📱 Alternative: Get Phone Number ID from Meta Console

If the script doesn't work, go here manually:

1. Open: https://developers.facebook.com
2. Click on "Property Engine Sudonum" app
3. Left sidebar → Click "WhatsApp"
4. Click "API Setup"
5. Look for "Phone number ID" in Step 1

It will look like:
```
┌─────────────────────────────────────┐
│ Step 1: Select phone number          │
│                                       │
│ Phone: +27 XX XXX XXXX               │
│ Phone number ID: 123456789012345 ← COPY THIS
│                                       │
└─────────────────────────────────────┘
```

---

## 🔥 Quick Start Commands

After getting Phone Number ID:

```bash
# 1. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Find Phone Number ID
python find_phone_number_id.py

# 3. Update .env with the output

# 4. Test everything
python test_setup.py

# 5. Add yourself as test user
python add_test_user.py

# 6. Send test message
python -m src.scheduler --once --mock
```

---

## ❗ Important Notes

### About the Access Token:
- **Temporary tokens** expire after 24 hours
- You'll need to generate a new one daily
- Or convert to a permanent token (see Meta docs)

### About Phone Number ID:
- This is **NOT** your phone number (+27...)
- It's a Meta-generated ID (looks like: 123456789012345)
- Each WhatsApp Business phone has a unique ID

### About Business Account ID:
- Might be the same as App ID (451967794668922)
- Or might be different (check in WhatsApp settings)
- The script will help you find the correct one

---

## 🆘 Troubleshooting

**Script says "No phone numbers found"**
→ Go to Meta console and add a WhatsApp phone number to your app

**"Invalid access token"**
→ Token expired or wrong. Generate a new one from Meta console

**"Permission denied"**
→ Token doesn't have `whatsapp_business_messaging` permission

---

## 🎉 That's It!

The script `find_phone_number_id.py` will do all the hard work. Just:
1. Run it
2. Copy the output
3. Paste into .env
4. Test with `test_setup.py`

You're 5 minutes away from sending WhatsApp messages! 🚀
