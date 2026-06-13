# ThreadWise – Intelligent Email Reply Agent

[![Azure Deployment](https://img.shields.io/badge/Azure-Deployed-blue)](https://threadwise-e6cwg2gke5djewe9.malaysiawest-01.azurewebsites.net/)
[![GitHub license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Tagline:** *Read the full story. Reply with confidence.*

ThreadWise is an AI-powered email reply agent built for the **Enterprise Agents for Microsoft 365 Copilot** hackathon track. It reads entire email threads, summarizes conversation history, scans attached documents (including password‑protected files), and automatically drafts context‑aware replies – all inside your existing Outlook workflow.

---

## ✨ Key Capabilities

- **Full‑thread comprehension** – Retrieves every message in a conversation, not just the latest one.
- **Document scanning** – Extracts text from PDF, Word, and Excel attachments; supports password‑protected files (password can be provided in email subject or securely via Azure Key Vault).
- **Intelligent summarization** – Generates a concise, bullet‑point summary highlighting decisions, action items, and open questions.
- **One‑click draft reply** – Produces a polished draft that answers the latest email while maintaining thread context and tone.
- **Enterprise‑grade security** – Leverages Microsoft Graph API with application permissions and integrates with Azure Key Vault for credential management.

---

## 🧠 How It Works

1. **Trigger** – User calls the `/trigger` endpoint (or webhook / polling).
2. **Fetch email thread** – Agent retrieves the full conversation via Microsoft Graph API.
3. **Process attachments** – Downloads and decrypts files (PDF, DOCX, XLSX) using provided passwords.
4. **AI reasoning (Work IQ)** – Sends thread + attachment content to Azure OpenAI with a prompt that mimics Microsoft’s Work IQ layer.
5. **Generate output** – Returns a structured summary and a draft reply.
6. **Save draft** – Creates a draft email in the user’s Outlook Drafts folder.

---

## 🏗️ Architecture
[User] → /trigger → Flask App (Azure App Service) → Graph API (emails/attachments)
↓
Azure OpenAI (Work IQ)
↓
Draft reply created in Outlook

text

- **Frontend**: Flask web app (Python)
- **Authentication**: Azure AD (client credentials flow – application permissions)
- **Email/Attachment access**: Microsoft Graph API
- **AI Engine**: Azure OpenAI (gpt-4o-mini) with Work‑IQ aligned prompt
- **Hosting**: Azure App Service (Linux, Python 3.12)
- **Secrets**: Azure Key Vault (optional) / Environment variables

---

## 🚀 Deployment Guide

### Prerequisites

- [Azure subscription](https://azure.microsoft.com/en-us/free/) (free tier works)
- [Microsoft 365 work/school account](https://developer.microsoft.com/en-us/microsoft-365/dev-program) with Exchange Online license
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed locally
- [Git](https://git-scm.com/) and [Python 3.12+](https://www.python.org/downloads/)

### 1. Clone or download the repository

```bash
git clone https://github.com/Junyao95/ThreadWise.git
cd ThreadWise
2. Create a virtual environment and install dependencies
bash
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
# or `venv\Scripts\activate` on CMD
pip install -r requirements.txt
3. Configure Azure AD app registration
In Azure portal, create an App Registration.

Add application permissions (not delegated): Mail.Read.All, Mail.ReadWrite.All, Mail.Send.All, User.Read.All.

Grant admin consent.

Record client_id, tenant_id, and create a client_secret.

4. Configure Exchange Online application access policy
Run these PowerShell commands as an admin:

powershell
Install-Module ExchangeOnlineManagement -Force
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
Import-Module ExchangeOnlineManagement
Connect-ExchangeOnline
New-ApplicationAccessPolicy -AppId <your_client_id> -PolicyScopeGroupId <user_email@tenant.onmicrosoft.com> -AccessRight RestrictAccess -Description "Restrict to specific mailbox"
5. Set environment variables in Azure App Service
Create a Web App on Azure (Linux, Python 3.12). Add the following App Settings:

Name	Value
AZURE_CLIENT_ID	Your app’s client ID
AZURE_TENANT_ID	Your tenant ID
AZURE_CLIENT_SECRET	Your client secret
AZURE_OPENAI_ENDPOINT	https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY	Your Azure OpenAI key
AZURE_OPENAI_DEPLOYMENT_NAME	gpt-4.1-mini (or your deployment name)
USER_EMAIL	The mailbox the agent will read (e.g., agent@yourtenant.onmicrosoft.com)
WEBSITES_PORT	8000
SCM_DO_BUILD_DURING_DEPLOYMENT	true
6. Deploy the code
Create a zip of the project (excluding .venv, __pycache__, .env, threadwise-agent.zip):

bash
powershell.exe -Command "Get-ChildItem -Path '.\' -Exclude '.venv','__pycache__','.env','threadwise-agent.zip' | Compress-Archive -DestinationPath '.\threadwise-agent.zip' -Force"
Then deploy:

bash
az webapp deploy --resource-group <your-rg> --name ThreadWise --src-path ./threadwise-agent.zip --type zip
7. Test the agent
Send a test email thread (with optional attachment) to the USER_EMAIL mailbox. Then visit:

text
https://threadwise-e6cwg2gke5djewe9.malaysiawest-01.azurewebsites.net/trigger
Check your Outlook Drafts folder – a reply draft will appear. View the logs with:

bash
az webapp log tail --resource-group <your-rg> --name ThreadWise
🔐 Handling Password‑Protected Attachments
Hackathon mode: Include the password in the email subject, e.g., [PWD:secret123] Your subject here. The agent extracts it and uses pypdf or msoffcrypto-tool to decrypt.

Enterprise mode: Integrate Azure Key Vault to retrieve passwords based on sender or document name.

📂 Project Structure
text
threadwise-agent/
├── app.py                     # Flask endpoints (/, /trigger, /webhook)
├── agent.py                   # Main orchestration logic
├── graph_client.py            # Microsoft Graph API wrapper
├── ai_engine.py               # Azure OpenAI (Work IQ) integration
├── document_processor.py      # Decryption & text extraction for PDF/Word/Excel
├── requirements.txt           # Python dependencies
├── .env                       # Local secrets (ignored by git)
├── .gitignore                 # Excludes venv, .env, zip, etc.
└── README.md                  # This file
🛠️ Tech Stack
Component	Technology
Backend	Python 3.12, Flask, Gunicorn
Cloud Hosting	Azure App Service (Linux)
Authentication	Microsoft Entra ID (Azure AD)
Email & Calendar	Microsoft Graph API
AI Models	Azure OpenAI (gpt-4.1-mini) with Work IQ alignment
Document Decryption	pypdf, msoffcrypto-tool
Deployment	Azure CLI, zip deploy
🤝 Contributing
This project was built for the Microsoft AI Agent Hackathon 2026 (Enterprise Agents for Microsoft 365 Copilot track). Not open for external contributions at this time.

📧 Contact
Author: Jun Yao Phoon

GitHub: @Junyao95

Project Repository: https://github.com/Junyao95/ThreadWise

🙏 Acknowledgements
Microsoft Graph API documentation

Azure OpenAI service

Oryx build system for Python on App Service

Open source libraries: msal, pypdf, msoffcrypto-tool, Flask, gunicorn

Built with ❤️ for the Microsoft AI Agent Hackathon 2026
