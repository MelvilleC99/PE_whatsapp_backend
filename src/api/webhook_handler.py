"""
WhatsApp Webhook Handler - API Layer
Receives incoming webhook requests from Meta/WhatsApp
"""
import threading
import time
from flask import Flask, request, jsonify
from loguru import logger

from src.config import settings
from src.agent.orchestrator import Orchestrator

app = Flask(__name__)

# Lazy load orchestrator
orchestrator = None

# Simple deduplication cache (message_id -> timestamp)
processed_messages = {}
DEDUP_WINDOW = 300  # 5 minutes


def get_orchestrator():
    """Lazy load orchestrator to avoid initialization issues"""
    global orchestrator
    if orchestrator is None:
        orchestrator = Orchestrator()
    return orchestrator


def is_duplicate(message_id: str) -> bool:
    """Check if message was already processed"""
    global processed_messages
    
    # Clean old entries
    now = time.time()
    processed_messages = {k: v for k, v in processed_messages.items() if now - v < DEDUP_WINDOW}
    
    if message_id in processed_messages:
        logger.warning(f"⚠️ Duplicate message {message_id} - skipping")
        return True
    
    processed_messages[message_id] = now
    return False


@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Webhook verification for Meta"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    logger.info(f"Webhook verification attempt - mode: {mode}, token received: {token is not None}")
    
    if mode == 'subscribe' and token == settings.webhook_verify_token:
        logger.info("✅ Webhook verified successfully")
        return challenge, 200
    else:
        logger.warning(f"❌ Webhook verification failed")
        return 'Forbidden', 403


def process_webhook_async(data: dict):
    """Process webhook in background thread"""
    try:
        orch = get_orchestrator()
        
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                if change.get('value', {}).get('messages'):
                    for message in change['value']['messages']:
                        # Deduplicate
                        msg_id = message.get('id')
                        if msg_id and is_duplicate(msg_id):
                            continue
                        
                        logger.info(f"Processing message {msg_id} from {message.get('from')}")
                        orch.handle_message(message, change['value'])
                        
    except Exception as e:
        logger.error(f"❌ Background processing error: {e}")


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Handle incoming WhatsApp messages.
    Returns 200 immediately and processes in background.
    """
    try:
        data = request.get_json()
        logger.info(f"📨 Received webhook")
        
        # Quick validation
        if not data.get('entry'):
            return jsonify({'status': 'ok'}), 200
        
        # Check for status updates (not messages) - ignore these
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                if change.get('value', {}).get('statuses'):
                    logger.debug("Ignoring status update")
                    return jsonify({'status': 'ok'}), 200
        
        # Process in background thread - return 200 immediately
        thread = threading.Thread(target=process_webhook_async, args=(data,))
        thread.start()
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return jsonify({'status': 'ok'}), 200  # Still return 200 to prevent retries


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'whatsapp-webhook'
    }), 200


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
