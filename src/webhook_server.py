"""
WhatsApp Webhook Handler
Receives incoming messages and responds with insights
"""
from flask import Flask, request, jsonify
from loguru import logger
import hmac
import hashlib

from src.config import settings
from src.firebase_manager import FirebaseManager
from src.whatsapp_sender import WhatsAppSender
from src.utils import format_insight_message

app = Flask(__name__)

# Don't initialize services on startup - lazy load when needed
firebase = None
whatsapp = None


def get_firebase():
    """Lazy load Firebase"""
    global firebase
    if firebase is None:
        firebase = FirebaseManager()
    return firebase


def get_whatsapp():
    """Lazy load WhatsApp sender"""
    global whatsapp
    if whatsapp is None:
        whatsapp = WhatsAppSender()
    return whatsapp


@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Webhook verification for Meta
    Meta sends a GET request to verify your webhook
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    logger.info(f"Webhook verification attempt - mode: {mode}, token received: {token is not None}")
    
    if mode == 'subscribe' and token == settings.webhook_verify_token:
        logger.info("Webhook verified successfully")
        return challenge, 200
    else:
        logger.warning(f"Webhook verification failed - Expected token: {settings.webhook_verify_token}, Received: {token}")
        return 'Forbidden', 403


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Handle incoming WhatsApp messages
    """
    try:
        data = request.get_json()
        logger.info(f"Received webhook: {data}")
        
        # Extract message data
        if not data.get('entry'):
            return jsonify({'status': 'ok'}), 200
        
        for entry in data['entry']:
            for change in entry.get('changes', []):
                if change.get('value', {}).get('messages'):
                    for message in change['value']['messages']:
                        handle_incoming_message(message, change['value'])
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


def handle_incoming_message(message: dict, value: dict):
    """
    Process a single incoming message
    
    Args:
        message: Message object from webhook
        value: Value object containing metadata
    """
    try:
        # Extract details
        from_number = message.get('from')
        message_type = message.get('type')
        
        # Only handle text messages for now
        if message_type != 'text':
            logger.info(f"Ignoring non-text message type: {message_type}")
            return
        
        text = message.get('text', {}).get('body', '').strip().lower()
        
        logger.info(f"Message from {from_number}: {text}")
        
        # Look up user in Firebase
        fb = get_firebase()
        user = fb.get_user_by_phone(from_number)
        
        if not user:
            handle_unregistered_user(from_number, text)
            return
        
        # User exists - handle their request
        handle_registered_user(user, text, from_number)
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")


def handle_registered_user(user: dict, text: str, phone: str):
    """
    Handle message from registered user
    
    Args:
        user: User document from Firebase
        text: Message text (lowercase)
        phone: User's phone number
    """
    # ONLY respond to insights requests - ignore everything else
    if 'insight' in text or 'report' in text or 'stats' in text:
        send_user_insights(user, phone)
    else:
        # Log but don't respond to any other messages
        logger.info(f"Ignoring non-insights message from {user['name']}: {text}")


def send_user_insights(user: dict, phone: str):
    """
    Send insights to registered user
    """
    try:
        # Get saved insights from Firebase
        fb = get_firebase()
        insights_doc = fb.get_insights(user['id'])
        
        if not insights_doc or not insights_doc.get('data'):
            wa = get_whatsapp()
            wa.send_text_message(
                phone,
                f"Hi {user['name']}! 👋\n\nNo insights available yet. We'll send your first report soon!"
            )
            return
        
        # Format and send insights
        insights = insights_doc['data']
        message = format_insight_message(insights, user['name'])
        
        wa = get_whatsapp()
        wa.send_text_message(phone, message)
        logger.success(f"Sent insights to {user['name']} ({phone})")
        
    except Exception as e:
        logger.error(f"Failed to send insights: {e}")
        wa = get_whatsapp()
        wa.send_text_message(
            phone,
            "Sorry, there was an error retrieving your insights. Please try again later."
        )


def handle_unregistered_user(phone: str, text: str):
    """
    Handle message from unregistered user
    
    Args:
        phone: User's phone number
        text: Message text (lowercase)
    """
    # Ignore all messages from unregistered users
    logger.info(f"Ignoring message from unregistered user {phone}: {text}")


def send_signup_message(phone: str):
    """
    Send signup instructions
    """
    message = """
📊 *Welcome to Property Insights!*

To complete your signup, please provide:
1. Your full name
2. Your company name (if applicable)

Reply with your details and we'll get you set up!

Example: "John Smith, ABC Properties"
    """.strip()
    
    whatsapp.send_text_message(phone, message)


def handle_unsubscribe(user: dict, phone: str):
    """
    Handle unsubscribe request
    """
    try:
        # Deactivate user
        firebase.delete_user(user['id'])
        
        whatsapp.send_text_message(
            phone,
            f"Sorry to see you go, {user['name']}! 👋\n\nYou've been unsubscribed from weekly insights.\n\nReply *SIGNUP* anytime to re-subscribe."
        )
        
        logger.info(f"Unsubscribed user: {user['name']} ({phone})")
        
    except Exception as e:
        logger.error(f"Failed to unsubscribe user: {e}")


def send_help_message(phone: str, name: str = None):
    """
    Send help/commands list
    """
    greeting = f"Hi {name}!" if name else "Hi there!"
    
    message = f"""
{greeting} 👋

*Available Commands:*

📊 *insights* - Get your latest insights
❓ *help* - Show this message
🛑 *stop* - Unsubscribe from insights

Just send me a message anytime and I'll send your latest insights!
    """.strip()
    
    whatsapp.send_text_message(phone, message)


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    
    print("=" * 70)
    print("WhatsApp Webhook Server")
    print("=" * 70)
    print()
    print(f"Starting server on port {port}...")
    print()
    
    if os.environ.get('ENVIRONMENT') == 'production':
        print("Running in PRODUCTION mode")
    else:
        print("To test locally with ngrok:")
        print("  1. Run: ngrok http 8080")
        print("  2. Copy the HTTPS URL")
        print("  3. Add to Meta: Settings → WhatsApp → Configuration")
        print("     Webhook URL: https://your-ngrok-url.ngrok.io/webhook")
        print("     Verify Token: mySecretToken123")
    print()
    
    app.run(host='0.0.0.0', port=port, debug=(os.environ.get('ENVIRONMENT') != 'production'))
