import os
import requests
import msal
from dotenv import load_dotenv

load_dotenv()

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
SCOPES = ["Mail.Read", "Mail.ReadWrite", "Mail.Send", "User.Read"]

class GraphClient:
    def __init__(self):
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.token = None

    def get_access_token(self) -> str:
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=authority
        )
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" in result:
            self.token = result["access_token"]
            return self.token
        else:
            raise RuntimeError(f"Authentication failed: {result.get('error_description', result)}")

    def _headers(self) -> dict:
        if not self.token:
            self.get_access_token()
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def get_latest_unread_emails(self, top: int = 10) -> list:
        params = {
            "$filter": "isRead eq false",
            "$select": "id,subject,from,receivedDateTime,bodyPreview,conversationId,hasAttachments",
            "$top": top,
            "$orderby": "receivedDateTime desc"
        }
        response = requests.get(
            f"{GRAPH_BASE}/users/junyaophoon7@outlook.com/mailFolders/inbox/messages",
            headers=self._headers(),
            params=params
        )
        response.raise_for_status()
        return response.json().get("value", [])

    def get_full_thread(self, conversation_id: str) -> list:
        params = {
            "$filter": f"conversationId eq '{conversation_id}'",
            "$orderby": "receivedDateTime asc",
            "$select": "id,subject,from,receivedDateTime,body,bodyPreview"
        }
        response = requests.get(
            f"{GRAPH_BASE}/me/messages",
            headers=self._headers(),
            params=params
        )
        response.raise_for_status()
        return response.json().get("value", [])

    def download_attachment(self, message_id: str, attachment_id: str) -> bytes:
        content_response = requests.get(
            f"{GRAPH_BASE}/me/messages/{message_id}/attachments/{attachment_id}/$value",
            headers=self._headers()
        )
        content_response.raise_for_status()
        return content_response.content

    def get_attachments_list(self, message_id: str) -> list:
        response = requests.get(
            f"{GRAPH_BASE}/me/messages/{message_id}/attachments",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json().get("value", [])

    def create_reply_draft(self, message_id: str, body_text: str) -> dict:
        payload = {
            "message": {
                "body": {
                    "contentType": "Text",
                    "content": body_text
                }
            }
        }
        response = requests.post(
            f"{GRAPH_BASE}/me/messages/{message_id}/createReply",
            headers=self._headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()