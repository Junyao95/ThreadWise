# ThreadWise – Video Script (3–4 minutes)

## Introduction (0:00–0:30)

**Visual:** Overflowing Outlook inbox, then cut to the live Azure home page (`https://threadwise-e6cwg2gke5djewe9.malaysiawest-01.azurewebsites.net`).

**Audio:**  
Email shouldn’t be a second full‑time job. I built **ThreadWise** – an intelligent email reply agent for the Microsoft 365 Copilot ecosystem. It reads the full thread, scans every attachment, and creates a draft reply – all automatically. No Outlook extension needed.

---

## Problem & Solution (0:30–1:00)

**Visual:** Show a long email thread (screen recording) with multiple replies and attachments.

**Audio:**  
Enterprise professionals waste hours scrolling through long threads, re‑reading decisions, and searching for attachments. ThreadWise solves this by using **Work IQ** – Microsoft’s intelligence layer for understanding email context, people relationships, and documents.

---

## Live Demo (1:00–2:30)

**Visual:** Split screen – left: terminal / Outlook mailbox, right: browser.

**Audio:**  
Let me show you. I have deployed ThreadWise to Azure App Service. Here is the home page – it confirms the agent is running.

I now send a test email to the target mailbox. It contains a short thread and a password‑protected Excel file. The password is included in the email subject: `[PWD:budget2025]`.

Now I visit the **`/trigger`** endpoint. This tells ThreadWise to process the latest unread email.  
*(Click the URL – wait a few seconds)*

The agent has finished. Let me open Outlook Web Access – and there, in the **Drafts folder**, is the generated reply. It summarises the thread, references the attachment, and asks for next steps.  

The entire process took less than 10 seconds.

---

## Architecture & Security (2:30–3:00)

**Visual:** Simple diagram – `User → /trigger → Flask App → Graph API → Azure OpenAI (Work IQ) → Outlook Drafts`.

**Audio:**  
Under the hood, ThreadWise uses Microsoft Graph API with **application permissions** – so no user login is required. It calls Azure OpenAI with a custom prompt that aligns with Work IQ. The final draft is saved directly to Outlook. Attachments are decrypted using `pypdf` and `msoffcrypto‑tool`. Passwords can come from the email subject or, in an enterprise setup, from Azure Key Vault.

---

## Impact & Closing (3:00–3:30)

**Visual:** Bullet points on screen – “Up to 70% less email handling time”, “No attachment overlooked”, “Enterprise‑grade security”.

**Audio:**  
ThreadWise can reduce email handling time by up to 70%, ensure no critical attachment is missed, and deliver consistent, grounded replies – all while respecting enterprise security.  

The code is open source on GitHub, and the live agent is running at the URL below.  

If your team is drowning in email, ThreadWise gives that time back. Thank you.

---

## Links

- **Live agent:** `https://threadwise-e6cwg2gke5djewe9.malaysiawest-01.azurewebsites.net`
- **GitHub repo:** `https://github.com/Junyao95/ThreadWise`
