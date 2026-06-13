# agent.py
import os
import time
from graph_client import GraphClient
from document_processor import process_attachment
from ai_engine import AIEngine
from dotenv import load_dotenv

load_dotenv()

class ThreadWiseAgent:
    def __init__(self):
        self.graph = GraphClient()
        self.ai = AIEngine()
        self.processed_emails = set()  # Simple cache to avoid re-processing

    def extract_password_from_email(self, email_subject: str, email_body: str) -> str:
        """
        Hackathon mode: extract password from email subject or body.
        Format example: [PWD:mySecret123] or Password: mySecret123
        """
        # Method 1: Look for [PWD:...] in subject
        if "[PWD:" in email_subject:
            start = email_subject.find("[PWD:") + 5
            end = email_subject.find("]", start)
            if end != -1:
                return email_subject[start:end]
        # Method 2: Look for "Password:" in body
        lines = email_body.split("\n")
        for line in lines:
            if "Password:" in line or "password:" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    return parts[1].strip()
        return None

    def process_new_email(self, message: dict):
        """
        Process a single email message:
        1. Fetch full thread using conversationId
        2. Download and decrypt attachments
        3. Generate summary and reply via AI
        4. Create a draft reply in Outlook
        """
        message_id = message['id']
        if message_id in self.processed_emails:
            print(f"Email {message_id} already processed. Skipping.")
            return

        print(f"Processing email: {message['subject']}")

        # 1. Get full conversation thread
        conv_id = message.get('conversationId')
        if not conv_id:
            print("No conversationId found. Processing as single email.")
            thread = [message]
        else:
            thread = self.graph.get_full_thread(conv_id)
            print(f"Retrieved {len(thread)} messages in thread")

        # 2. Check for attachments in the latest email (or first unread)
        latest_msg_id = message['id']
        attachments_list = self.graph.get_attachments_list(latest_msg_id)
        attachments_text = {}

        # Hackathon mode: extract password from the email content
        password = self.extract_password_from_email(
            message.get('subject', ''),
            message.get('bodyPreview', '')
        )

        for attachment in attachments_list:
            if attachment.get('name'):
                filename = attachment['name']
                print(f"Downloading attachment: {filename}")
                content_bytes = self.graph.download_attachment(latest_msg_id, attachment['id'])
                try:
                    extracted_text = process_attachment(content_bytes, filename, password)
                    attachments_text[filename] = extracted_text[:3000]  # Limit length
                    print(f"Successfully extracted content from {filename}")
                except Exception as e:
                    print(f"Failed to process {filename}: {e}")
                    attachments_text[filename] = f"[Failed to decrypt: {e}]"

        # 3. Generate summary and draft reply
        print("Calling Azure OpenAI (Work IQ) to generate summary and reply...")
        result = self.ai.generate_summary_and_reply(thread, attachments_text)

        print("\n" + "="*50)
        print("SUMMARY:")
        print(result.get('summary', 'No summary generated'))
        print("="*50)
        print("DRAFT REPLY:")
        print(result.get('reply', 'No reply generated'))
        print("="*50)

        # 4. Create draft reply in Outlook
        try:
            draft = self.graph.create_reply_draft(latest_msg_id, result['reply'])
            print(f"✅ Draft reply created successfully! Draft ID: {draft.get('id')}")
            print(f"   User can review and send from Outlook Drafts folder.")
        except Exception as e:
            print(f"❌ Failed to create draft: {e}")

        # Mark as processed
        self.processed_emails.add(message_id)

    def run_polling_loop(self, interval_seconds: int = 60):
        """
        Continuously poll the inbox for new unread emails.
        For hackathon simplicity, this is a polling loop.
        """
        print(f"ThreadWise Agent started. Polling every {interval_seconds} seconds...")
        while True:
            try:
                print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking for new emails...")
                unread_emails = self.graph.get_latest_unread_emails(top=5)
                new_emails = [e for e in unread_emails if e['id'] not in self.processed_emails]

                for email in new_emails:
                    self.process_new_email(email)

                time.sleep(interval_seconds)
            except Exception as e:
                print(f"Error in polling loop: {e}")
                time.sleep(interval_seconds)

if __name__ == "__main__":
    agent = ThreadWiseAgent()
    # Run once for testing, then switch to polling
    # unread = agent.graph.get_latest_unread_emails(top=1)
    # if unread:
    #     agent.process_new_email(unread[0])
    # else:
    #     print("No unread emails found. Sending test email recommended.")
    agent.run_polling_loop(60)