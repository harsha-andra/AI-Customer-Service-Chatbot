"""
AI Customer Service Chatbot Engine
====================================
Business-independent chatbot backend supporting multiple cloud providers:
  - IBM Watson Assistant
  - Google Dialogflow
  - AWS Lex
  - OpenAI (GPT-4 / GPT-3.5)
  - Anthropic Claude API
  - Local / Open-Source (Ollama)

Configure your preferred provider in config/settings.yaml
"""

import os
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Load config
# ─────────────────────────────────────────────

def load_config(path: str = "config/settings.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ─────────────────────────────────────────────
# Cloud Provider Adapters
# ─────────────────────────────────────────────

class IBMWatsonAdapter:
    """IBM Watson Assistant adapter."""

    def __init__(self, cfg: dict):
        from ibm_watson import AssistantV2
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
        authenticator = IAMAuthenticator(cfg["api_key"])
        self.assistant = AssistantV2(version="2021-11-27", authenticator=authenticator)
        self.assistant.set_service_url(cfg["service_url"])
        self.assistant_id = cfg["assistant_id"]

    def create_session(self) -> str:
        resp = self.assistant.create_session(assistant_id=self.assistant_id).get_result()
        return resp["session_id"]

    def send_message(self, session_id: str, text: str) -> dict:
        resp = self.assistant.message(
            assistant_id=self.assistant_id,
            session_id=session_id,
            input={"message_type": "text", "text": text},
        ).get_result()
        output = resp.get("output", {})
        replies = [g["text"] for g in output.get("generic", []) if g.get("response_type") == "text"]
        intents = [i["intent"] for i in output.get("intents", [])]
        return {"reply": " ".join(replies), "intents": intents, "raw": resp}


class DialogflowAdapter:
    """Google Dialogflow CX/ES adapter."""

    def __init__(self, cfg: dict):
        from google.cloud import dialogflow_v2 as dialogflow
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cfg["credentials_path"]
        self.client = dialogflow.SessionsClient()
        self.project_id = cfg["project_id"]
        self.language = cfg.get("language", "en")

    def send_message(self, session_id: str, text: str) -> dict:
        from google.cloud import dialogflow_v2 as dialogflow
        session = self.client.session_path(self.project_id, session_id)
        text_input = dialogflow.TextInput(text=text, language_code=self.language)
        query_input = dialogflow.QueryInput(text=text_input)
        resp = self.client.detect_intent(request={"session": session, "query_input": query_input})
        result = resp.query_result
        return {
            "reply": result.fulfillment_text,
            "intents": [result.intent.display_name],
            "raw": str(result),
        }


class AWSLexAdapter:
    """AWS Lex V2 adapter."""

    def __init__(self, cfg: dict):
        import boto3
        self.client = boto3.client(
            "lexv2-runtime",
            region_name=cfg["region"],
            aws_access_key_id=cfg["access_key"],
            aws_secret_access_key=cfg["secret_key"],
        )
        self.bot_id = cfg["bot_id"]
        self.bot_alias_id = cfg["bot_alias_id"]
        self.locale_id = cfg.get("locale_id", "en_US")

    def send_message(self, session_id: str, text: str) -> dict:
        resp = self.client.recognize_text(
            botId=self.bot_id,
            botAliasId=self.bot_alias_id,
            localeId=self.locale_id,
            sessionId=session_id,
            text=text,
        )
        messages = [m["content"] for m in resp.get("messages", [])]
        intent = resp.get("sessionState", {}).get("intent", {}).get("name", "")
        return {"reply": " ".join(messages), "intents": [intent], "raw": resp}


class OpenAIAdapter:
    """OpenAI GPT adapter (GPT-4 / GPT-3.5-turbo)."""

    def __init__(self, cfg: dict):
        import openai
        openai.api_key = cfg["api_key"]
        self.model = cfg.get("model", "gpt-4o-mini")
        self.system_prompt = cfg.get("system_prompt", "You are a helpful business customer service assistant.")
        self.history = []

    def send_message(self, session_id: str, text: str) -> dict:
        import openai
        self.history.append({"role": "user", "content": text})
        resp = openai.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": self.system_prompt}] + self.history[-20:],
        )
        reply = resp.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return {"reply": reply, "intents": [], "raw": resp}


class AnthropicAdapter:
    """Anthropic Claude API adapter."""

    def __init__(self, cfg: dict):
        import anthropic
        self.client = anthropic.Anthropic(api_key=cfg["api_key"])
        self.model = cfg.get("model", "claude-3-haiku-20240307")
        self.system_prompt = cfg.get("system_prompt", "You are a helpful business customer service assistant.")
        self.history = []

    def send_message(self, session_id: str, text: str) -> dict:
        self.history.append({"role": "user", "content": text})
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=self.system_prompt,
            messages=self.history[-20:],
        )
        reply = resp.content[0].text
        self.history.append({"role": "assistant", "content": reply})
        return {"reply": reply, "intents": [], "raw": resp}


class OllamaAdapter:
    """Local Ollama (open-source models) adapter — no API cost."""

    def __init__(self, cfg: dict):
        import requests as req
        self.base_url = cfg.get("base_url", "http://localhost:11434")
        self.model = cfg.get("model", "llama3")
        self.system_prompt = cfg.get("system_prompt", "You are a helpful business customer service assistant.")
        self.req = req
        self.history = []

    def send_message(self, session_id: str, text: str) -> dict:
        self.history.append({"role": "user", "content": text})
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": self.system_prompt}] + self.history[-20:],
            "stream": False,
        }
        resp = self.req.post(f"{self.base_url}/api/chat", json=payload)
        reply = resp.json()["message"]["content"]
        self.history.append({"role": "assistant", "content": reply})
        return {"reply": reply, "intents": [], "raw": resp.json()}


# ─────────────────────────────────────────────
# Provider Factory
# ─────────────────────────────────────────────

PROVIDER_MAP = {
    "ibm_watson": IBMWatsonAdapter,
    "dialogflow": DialogflowAdapter,
    "aws_lex": AWSLexAdapter,
    "openai": OpenAIAdapter,
    "anthropic": AnthropicAdapter,
    "ollama": OllamaAdapter,
}


def get_provider(cfg: dict):
    provider = cfg["chatbot"]["provider"]
    if provider not in PROVIDER_MAP:
        raise ValueError(f"Unknown provider '{provider}'. Choose from: {list(PROVIDER_MAP.keys())}")
    provider_cfg = cfg["providers"][provider]
    return PROVIDER_MAP[provider](provider_cfg)


# ─────────────────────────────────────────────
# Email Notification (works with any email)
# ─────────────────────────────────────────────

def send_email_notification(cfg: dict, subject: str, body: str) -> bool:
    """
    Send a notification email when a customer submits a query/booking/request.
    Works with Gmail, Outlook, SendGrid SMTP, AWS SES, etc.
    """
    email_cfg = cfg.get("email", {})
    if not email_cfg.get("enabled", False):
        logger.info("Email notifications disabled.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = email_cfg["sender"]
        msg["To"] = email_cfg["recipient"]

        html_body = f"""
        <html><body style="font-family:sans-serif;padding:24px">
        <h2 style="color:#2563eb">📬 New Customer Enquiry</h2>
        <pre style="background:#f3f4f6;padding:16px;border-radius:8px">{body}</pre>
        <p style="color:#6b7280;font-size:12px">Sent by AI Customer Chatbot · {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </body></html>
        """
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(email_cfg["smtp_host"], email_cfg["smtp_port"]) as server:
            server.starttls()
            server.login(email_cfg["sender"], email_cfg["app_password"])
            server.sendmail(email_cfg["sender"], email_cfg["recipient"], msg.as_string())

        logger.info(f"Email sent to {email_cfg['recipient']}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


# ─────────────────────────────────────────────
# Chatbot Session Manager
# ─────────────────────────────────────────────

class ChatbotSession:
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.cfg = load_config(config_path)
        self.provider = get_provider(self.cfg)
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.conversation_log = []

        # IBM Watson needs a session token
        if hasattr(self.provider, "create_session"):
            self.session_id = self.provider.create_session()

    def chat(self, user_input: str) -> str:
        result = self.provider.send_message(self.session_id, user_input)
        reply = result["reply"]

        self.conversation_log.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "bot": reply,
            "intents": result.get("intents", []),
        })

        # Trigger email if a completion intent detected or keywords found
        trigger_keywords = self.cfg["chatbot"].get("email_trigger_keywords", [])
        if any(k.lower() in user_input.lower() for k in trigger_keywords):
            subject = f"[Chatbot] New customer enquiry — {datetime.now().strftime('%Y-%m-%d')}"
            body = f"User message:\n{user_input}\n\nBot reply:\n{reply}\n\nSession: {self.session_id}"
            send_email_notification(self.cfg, subject, body)

        return reply

    def save_log(self, path: Optional[str] = None):
        path = path or f"logs/session_{self.session_id}.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.conversation_log, f, indent=2)
        logger.info(f"Conversation saved to {path}")


# ─────────────────────────────────────────────
# CLI Quick Test
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=== AI Customer Chatbot ===")
    print("Type 'quit' to exit.\n")
    bot = ChatbotSession()
    while True:
        user = input("You: ").strip()
        if user.lower() in ("quit", "exit"):
            bot.save_log()
            break
        reply = bot.chat(user)
        print(f"Bot: {reply}\n")
