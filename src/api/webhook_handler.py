"""
WhatsApp Webhook Handler - API Layer
Receives incoming webhook requests from Meta/WhatsApp
"""
from flask import Flask, request, jsonify
from loguru import logger

from src.config import settings
from src.handlers.command_handler import CommandHandler

app = Flask(__name__)

# Lazy load command handler
command_handler = None


def get_command_handler():
    """Lazy load command handler to avoid initialization issues"""
    global command_handler
    if command_handler is None:
        command_handler = CommandHandler()
    return command_handler


@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Webhook verification for Meta
    Meta sends a GET request to verify your webhook URL
    
    Returns:
        challenge: The challenge string if verification succeeds
        403: If verification fails
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    logger.info(f"Webhook verification attempt - mode: {mode}, token received: {token is not None}")
    
    if mode == 'subscribe' and token == settings.webhook_verify_token:
        logger.info("✅ Webhook verified successfully")
        return challenge, 200
    else:
        logger.warning(
            f"❌ Webhook verification failed - "
            f"Expected token: {settings.webhook_verify_token}, "
            f"Received: {token}"
        )
        return 'Forbidden', 403


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Handle incoming WhatsApp messages
    
    Processes webhook events from Meta/WhatsApp and routes them
    to the appropriate command handler.
    
    Returns:
        200: Webhook processed successfully
        500: Server error during processing
    """
    try:
        data = request.get_json()
        logger.info(f"📨 Received webhook: {data}")
        
        # Extract message data
        if not data.get('entry'):
            return jsonify({'status': 'ok'}), 200
        
        # Get command handler
        handler = get_command_handler()
        
        # Process each entry and message
        for entry in data['entry']:
            for change in entry.get('changes', []):
                if change.get('value', {}).get('messages'):
                    for message in change['value']['messages']:
                        handler.handle_message(message, change['value'])
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring
    
    Returns:
        200: Service is healthy
    """
    return jsonify({
        'status': 'healthy',
        'service': 'whatsapp-webhook'
    }), 200


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    
    print("=" * 70)
    print("🚀 WhatsApp Webhook Server")
    print("=" * 70)
    print()
    print(f"Starting server on port {port}...")
    print()
    
    if os.environ.get('ENVIRONMENT') == 'production':
        print("Running in PRODUCTION mode 🏭")
    else:
        print("Running in DEVELOPMENT mode 🛠️")
        print()
        print("To test locally with ngrok:")
        print("  1. Run: ngrok http 8080")
        print("  2. Copy the HTTPS URL")
        print("  3. Add to Meta: Settings → WhatsApp → Configuration")
        print("     Webhook URL: https://your-ngrok-url.ngrok.io/webhook")
        print(f"     Verify Token: {settings.webhook_verify_token}")
    print()
    print("=" * 70)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=(os.environ.get('ENVIRONMENT') != 'production')
    )
