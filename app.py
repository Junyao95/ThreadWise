# app.py
import os
from flask import Flask, request, jsonify
from agent import ThreadWiseAgent
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
agent = ThreadWiseAgent()

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """
    Microsoft Graph change notification webhook endpoint.
    - GET request: validationToken response for subscription setup.
    - POST request: actual email change notification.
    """
    if request.method == 'GET':
        # Graph sends validationToken during webhook subscription creation
        validation_token = request.args.get('validationToken')
        if validation_token:
            return validation_token, 200
        return "Webhook ready", 200

    elif request.method == 'POST':
        # Process incoming change notification
        notifications = request.json
        try:
            # Each notification contains details of changed resource
            for notification in notifications.get('value', []):
                # Parse the resource data (you would need to fetch full email details via Graph)
                # For hackathon simplicity, we trigger the polling loop instead.
                logging.info(f"Received notification: {notification.get('resource')}")
                # Trigger processing of the latest email
                unread = agent.graph.get_latest_unread_emails(top=1)
                if unread:
                    agent.process_new_email(unread[0])
        except Exception as e:
            logging.error(f"Webhook processing error: {e}")

        return "OK", 200

@app.route('/')
def home():
    return "ThreadWise Agent is running. Use /webhook for Graph notifications."

@app.route('/trigger', methods=['GET'])
def trigger():
    """Manually trigger processing of the latest unread email."""
    try:
        unread = agent.graph.get_latest_unread_emails(top=1)
        if unread:
            agent.process_new_email(unread[0])
            return "✅ Agent triggered. Check logs and Outlook Drafts folder.", 200
        else:
            return "📭 No unread emails found.", 200
    except Exception as e:
        logging.error(f"Trigger error: {e}")
        return f"❌ Error: {e}", 500
        
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)