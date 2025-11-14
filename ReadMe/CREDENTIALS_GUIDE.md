# 🔑 Understanding Meta WhatsApp Credentials

## What You Have vs What We Need

### 📋 Your Current Info:
```
App Name: Property Engine Sudonum
App ID: 451967794668922
```

You also mentioned:
- ✅ Business Account ID
- ✅ Business Secret (App Secret)
- ✅ Temporary Access Token
- ✅ Client ID (same as App ID)
- ✅ Client Secret (same as App Secret)

---

## 🎯 N8N vs Direct API Approach

### How N8N Works:
```
You give N8N:
  ├─ Client ID (App ID)
  └─ Client Secret (App Secret)
       ↓
N8N does OAuth flow automatically
       ↓
N8N gets Access Token for you
       ↓
N8N finds Phone Number ID for you
       ↓
Everything works!
```

### How Our Code Works:
```
You give us directly:
  ├─ Access Token (already have)
  ├─ Business Account ID (already have)
  └─ Phone Number ID (need to find)
       ↓
We call Meta API directly
       ↓
Everything works!
```

**The difference:** N8N does steps 1-2 automatically. We skip OAuth and go straight to using the token.

---

## 🔍 Finding Your Phone Number ID

### Method 1: Use Our Helper Script
```bash
python find_phone_number_id.py
```
Enter your App ID and Access Token, it will show you the Phone Number ID!

### Method 2: Meta Developer Console
1. Go to https://developers.facebook.com
2. Select your app (Property Engine Sudonum)
3. Click "WhatsApp" in left sidebar
4. Click "API Setup"
5. Look for this section:

```
Step 1: Select phone number
┌─────────────────────────────────────┐
│ Phone number: +27 XX XXX XXXX       │
│ Phone number ID: 123456789012345    │ ← THIS IS WHAT YOU NEED!
│ WhatsApp Business Account ID: XXX   │
└─────────────────────────────────────┘
```

### Method 3: API Call (Manual)
```bash
curl -X GET \
  "https://graph.facebook.com/v18.0/451967794668922/phone_numbers" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

This returns:
```json
{
  "data": [
    {
      "id": "123456789012345",  ← Phone Number ID
      "display_phone_number": "+27 XX XXX XXXX"
    }
  ]
}
```

---

## 📝 What Goes in .env File

Once you have everything, your `.env` should look like:

```bash
# Meta WhatsApp Business API Credentials
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_BUSINESS_ACCOUNT_ID=451967794668922
META_APP_ID=451967794668922
META_APP_SECRET=your_app_secret_here

# Note: Business Account ID might be different from App ID
# Check in WhatsApp → API Setup for the actual Business Account ID
```

---

## 🤔 Common Confusions

### "Business Account ID" vs "App ID"
- **App ID**: 451967794668922 (your app's identifier)
- **Business Account ID**: Usually different, found in WhatsApp settings
- For our purposes, we need the **WhatsApp Business Account ID**

### "Phone Number ID" vs "Phone Number"
- **Phone Number**: +27 XX XXX XXXX (what users see)
- **Phone Number ID**: 123456789012345 (Meta's internal ID)
- We need the **Phone Number ID** for API calls

---

## ✅ Quick Test After Setup

Once you have all credentials in `.env`:

```bash
# Test 1: Verify config loads
python -m src.config

# Test 2: Test WhatsApp connection
python -m src.whatsapp_sender
```

If both pass, you're ready to send messages! 🚀

---

## 🆘 If Token is Expired

Your temporary token lasts 24 hours. To get a new one:

1. Go to https://developers.facebook.com
2. Select your app
3. WhatsApp → API Setup
4. Find "Temporary access token"
5. Click "Generate" 
6. Copy new token to `.env`

### For Permanent Token:
- Temporary tokens expire in 24 hours
- System tokens last 60 days
- Never-expiring tokens: Need to create a System User

---

## 🎯 What You Need to Do NOW

1. **Run this command:**
   ```bash
   python find_phone_number_id.py
   ```

2. **Enter when prompted:**
   - App ID: `451967794668922`
   - Access Token: (your temporary token)

3. **Copy the output to your .env file**

4. **Test it:**
   ```bash
   python test_setup.py
   ```

That's it! 🎉

---

## 💡 Pro Tip

The script `find_phone_number_id.py` will automatically format the correct values for your `.env` file. Just copy-paste what it outputs!
