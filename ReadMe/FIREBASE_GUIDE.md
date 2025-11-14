# 🔥 Firebase Collections Guide

## What Collections Do We Need?

We need **2 collections** in Firestore:

### 1. `whatsapp_users` Collection
**Purpose:** Store all users who receive WhatsApp insights

**Structure:**
```
whatsapp_users/
  └─ user_doc_1/
      ├─ name: "John Smith"
      ├─ phone: "27821234567"           # E.164 format
      ├─ frequency: "weekly"             # weekly, daily, or monthly
      ├─ active: true                    # true = receives messages
      ├─ created_at: timestamp
      └─ last_sent: timestamp            # when last message was sent
```

**Example Document:**
```json
{
  "name": "John Smith",
  "phone": "27821234567",
  "frequency": "weekly",
  "active": true,
  "created_at": "2025-11-13T10:00:00Z",
  "last_sent": "2025-11-06T09:00:00Z"
}
```

---

### 2. `insights` Collection
**Purpose:** Store generated insights for each user (overwritten weekly)

**Structure:**
```
insights/
  └─ user_doc_1/                         # Same ID as user document
      ├─ user_id: "user_doc_1"
      ├─ generated_at: timestamp
      └─ data:
          ├─ sales_change: "+5%"
          ├─ active_listings: 45
          ├─ avg_price: "R450K"
          └─ sales_velocity: "12 days"
```

**Example Document:**
```json
{
  "user_id": "abc123xyz",
  "generated_at": "2025-11-13T09:00:00Z",
  "data": {
    "sales_change": "+5%",
    "active_listings": 45,
    "avg_price": "R450K",
    "sales_velocity": "12 days"
  }
}
```

---

## 🎯 How The System Works

### 1. Add Users
```python
from src.firebase_manager import FirebaseManager

fm = FirebaseManager()
fm.add_user(
    phone="27821234567",
    name="John Smith",
    frequency="weekly"
)
```

This creates a document in `whatsapp_users`

### 2. Generate Insights (Weekly Job)
```python
from src.insight_generator import InsightGenerator

ig = InsightGenerator()
insights = ig.generate_insights_for_user("user_123")

# Returns:
{
    "sales_change": "+5%",
    "active_listings": 45,
    "avg_price": "R450K",
    "sales_velocity": "12 days"
}
```

### 3. Save Insights to Firebase
```python
fm.save_insights(user_id="abc123xyz", insights_data=insights)
```

This creates/overwrites document in `insights` collection

### 4. Send via WhatsApp
```python
from src.whatsapp_sender import WhatsAppSender
from src.utils import format_insight_message

sender = WhatsAppSender()
message = format_insight_message(insights, "John Smith")
sender.send_text_message("27821234567", message)
```

Sends:
```
📊 *Weekly Property Insights for John Smith*

📈 Sales: +5%
🏠 Active Listings: 45
💰 Avg Price: R450K
⚡ Sales Velocity: 12 days

_Generated on 13 November 2025_
```

---

## 🚀 Setup Firebase Collections

### Option 1: Automatic (Recommended)
```bash
python setup_firebase.py
```

This script will:
- ✅ Connect to your Firebase project
- ✅ Create both collections
- ✅ Add example documents
- ✅ Show you the structure

### Option 2: Manual (Using Firebase Console)

1. Go to: https://console.firebase.google.com
2. Select project: `proptech-email-management`
3. Click "Firestore Database" in left menu
4. Click "Start collection"
5. Collection ID: `whatsapp_users`
6. Add first document:
   - Document ID: (auto-generate)
   - Fields:
     ```
     name (string): "Test User"
     phone (string): "27821234567"
     frequency (string): "weekly"
     active (boolean): false
     created_at (timestamp): now
     last_sent (timestamp): null
     ```
7. Repeat for `insights` collection

### Option 3: Add Users Programmatically
```bash
python add_test_user.py
```

This will:
- Ask for name and phone
- Create user in Firebase
- Collections auto-created on first document

---

## 📊 Example Firebase Structure

After setup, your Firestore will look like:

```
📁 Firestore Database
  │
  ├─ 📁 whatsapp_users (collection)
  │   ├─ 📄 abc123 (document)
  │   │   ├─ name: "John Smith"
  │   │   ├─ phone: "27821234567"
  │   │   ├─ frequency: "weekly"
  │   │   ├─ active: true
  │   │   ├─ created_at: timestamp
  │   │   └─ last_sent: timestamp
  │   │
  │   └─ 📄 xyz789 (document)
  │       ├─ name: "Jane Doe"
  │       └─ ...
  │
  └─ 📁 insights (collection)
      ├─ 📄 abc123 (document - same ID as user)
      │   ├─ user_id: "abc123"
      │   ├─ generated_at: timestamp
      │   └─ data: { ... }
      │
      └─ 📄 xyz789 (document)
          └─ ...
```

---

## 🔄 Weekly Flow

### Monday 9 AM (Scheduled Job):

1. **Fetch users**
   ```python
   users = fm.get_all_active_users()
   # Returns all users where active=true
   ```

2. **For each user:**
   - Generate insights from database
   - Save to `insights` collection (overwrites previous week)
   - Format message
   - Send via WhatsApp
   - Update `last_sent` timestamp

3. **Result:**
   - All active users get fresh insights
   - Old insights overwritten (saves Firestore storage)
   - System tracks when each user was last sent

---

## 💡 Field Explanations

### whatsapp_users fields:

- **name**: Display name in messages
- **phone**: Must be E.164 format (27821234567, not +27 or 0821...)
- **frequency**: How often to send (weekly/daily/monthly)
- **active**: 
  - `true` = user receives messages
  - `false` = user paused (won't receive)
- **created_at**: When user signed up
- **last_sent**: When we last sent them insights (prevents duplicates)

### insights fields:

- **user_id**: Links back to user document
- **generated_at**: When insights were calculated
- **data**: Flexible object - add any metrics you want!
  - Sales metrics
  - Listing stats
  - Performance indicators
  - Custom KPIs

---

## 🎨 Customizing Insights

Want to add more metrics? Easy!

### 1. Update insight_generator.py
Add your calculation:
```python
def _get_new_metric(self, cursor, user_id):
    query = "SELECT COUNT(*) FROM new_table WHERE ..."
    cursor.execute(query, (user_id,))
    return cursor.fetchone()[0]
```

### 2. Include in insights:
```python
insights = {
    "sales_change": sales_change,
    "active_listings": active_listings,
    "avg_price": avg_price,
    "sales_velocity": sales_velocity,
    "new_metric": new_metric,  # ← Add here
}
```

### 3. Update message template (utils.py):
```python
if "new_metric" in insights:
    message += f"🎯 New Metric: {insights['new_metric']}\n"
```

That's it! New metric flows through the entire system.

---

## 🧪 Testing Collections

```bash
# 1. Setup collections with examples
python setup_firebase.py

# 2. Verify Firebase connection
python test_setup.py

# 3. Add real user
python add_test_user.py

# 4. Send test insight (with mock data)
python -m src.scheduler --once --mock
```

---

## 📱 View in Firebase Console

After setup, view your data:

1. Go to: https://console.firebase.google.com
2. Select: `proptech-email-management`
3. Click: "Firestore Database"
4. Browse: `whatsapp_users` and `insights` collections

You'll see all documents, can edit manually, delete, etc.

---

## ✅ Ready to Setup?

Run this now:
```bash
python setup_firebase.py
```

It will guide you through creating the collections! 🎉
