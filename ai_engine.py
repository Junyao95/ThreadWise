# ai_engine.py
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

class AIEngine:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-10-21"
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")

    def _build_work_iq_prompt(self, thread_messages: list, attachments_text: dict) -> tuple:
        """
        Build a system prompt and user prompt that aligns with Work IQ principles.
        Returns (system_prompt, user_prompt)
        """
        system_prompt = """You are an AI assistant with Work IQ – Microsoft's intelligence layer for understanding work context, email threads, people relationships, and documents. Your task is to:
1. Analyze the entire email thread below, understanding who said what, decisions made, open questions, and action items.
2. If documents were attached and their content is provided, incorporate that information into your understanding.
3. Generate a concise, bullet-point summary of the thread, highlighting:
   - Key decisions or agreements
   - Outstanding questions or action items
   - Important context the user should know before replying
4. Then, draft a polite, professional reply to the LATEST email in the thread.
   - The reply should answer the latest message directly.
   - Maintain the same tone as the original conversation.
   - Include any relevant information from the thread summary or documents.
   - Do NOT repeat the entire thread history in the reply.

Format your response as:

SUMMARY:
- [point 1]
- [point 2]
...

REPLY:
[Your full email draft here]"""

        user_prompt = "Here is the email thread:\n\n"
        for msg in thread_messages:
            sender = msg.get('from', {}).get('emailAddress', {}).get('address', 'Unknown')
            subject = msg.get('subject', 'No subject')
            body = msg.get('bodyPreview', msg.get('body', {}).get('content', 'No content'))
            user_prompt += f"--- From: {sender}\nSubject: {subject}\nContent: {body}\n\n"

        if attachments_text:
            user_prompt += "\nAttached Documents Content:\n"
            for filename, content in attachments_text.items():
                user_prompt += f"--- {filename} ---\n{content[:2000]}\n"  # Truncate for token limits

        return system_prompt, user_prompt

    def generate_summary_and_reply(self, thread_messages: list, attachments_text: dict) -> dict:
        """
        Use Azure OpenAI to generate a summary and a draft reply.
        Returns a dict with 'summary' and 'reply' keys.
        """
        system_prompt, user_prompt = self._build_work_iq_prompt(thread_messages, attachments_text)

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        result_text = response.choices[0].message.content
        # Parse the response
        summary = ""
        reply = ""
        if "SUMMARY:" in result_text and "REPLY:" in result_text:
            parts = result_text.split("REPLY:")
            summary_part = parts[0].replace("SUMMARY:", "").strip()
            reply_part = parts[1].strip()
            summary = summary_part
            reply = reply_part
        else:
            # Fallback: treat entire response as reply
            reply = result_text

        return {"summary": summary, "reply": reply}