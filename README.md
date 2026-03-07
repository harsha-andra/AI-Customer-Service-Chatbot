# 🤖 AI Customer Service Chatbot

A **business-independent**, cloud-flexible AI chatbot for handling customer queries, appointments, complaints, and support — deployable with **6 different AI providers** in minutes.

************************************************************************************************************
<img src="https://raw.githubusercontent.com/harsha-andra/Ai-Customer_service-Chatbot/docs/demo.gif" alt="Demo">
************************************************************************************************************

-------------------------------------------------------------------------------------------------------------
<img src="[docs/demo-2.gif](https://raw.githubusercontent.com/harsha-andra/Ai-Customer_service-Chatbot/docs/demo-2.gif)" alt="Demo">
-------------------------------------------------------------------------------------------------------------

## ✨ Features

- 🌐 **Multi-cloud support** — IBM Watson, Google Dialogflow, AWS Lex, OpenAI, Anthropic Claude, or local Ollama
- 🏢 **Business-independent** — configure once for any business type (hotels, clinics, restaurants, e-commerce, SaaS)
- 💬 **Real-time chat UI** — clean, responsive web frontend, works on mobile and desktop
- 📧 **Email notifications** — auto-email the business owner when a customer submits a booking or complaint
- 🔒 **Privacy-first option** — run 100% locally with Ollama (no API costs, no data leaving your machine)
- 🗂️ **Conversation logging** — every session saved as JSON for analytics and audit
- ⚡ **Quick-reply buttons** — pre-built shortcuts for common customer actions
- 🔄 **Easy provider switching** — swap AI providers by changing one line in `config/settings.yaml`

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| **AI Providers** | IBM Watson · Google Dialogflow · AWS Lex · OpenAI · Anthropic · Ollama |
| **Backend** | Python · Flask · PyYAML |
| **Frontend** | HTML5 · CSS3 · Vanilla JS |
| **Notifications** | SMTP (Gmail / Outlook / AWS SES / SendGrid) |
| **Logging** | JSON session logs |

---

## 📂 Project Structure

```
ai-customer-chatbot/
├── backend/
│   ├── chatbot_engine.py   # Multi-cloud provider adapters + session manager
│   └── app.py              # Flask REST API
├── frontend/
│   └── index.html          # Chat UI (single-file, zero dependencies)
├── config/
│   └── settings.yaml       # All configuration — provider keys, business info, email
├── docs/
│   └── demo.gif            # Animated demo
├── scripts/
│   └── generate_demo_gif.py
└── requirements.txt
```

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/ai-customer-chatbot.git
cd ai-customer-chatbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Choose your AI provider

Open `config/settings.yaml` and set:

```yaml
chatbot:
  provider: ollama        # ← change this
  business_name: "My Café"
  bot_name: "Aria"
```

### 4. Fill in provider credentials

Only fill in the section that matches your chosen provider (see below).

### 5. Run the server

```bash
python backend/app.py
```

Open `http://localhost:5000` — your chatbot is live. ✅

---

## ☁️ Provider Setup Guides

<details>
<summary><strong>🆓 Ollama (Local — Free, no API cost)</strong></summary>

Best for: privacy, zero cost, offline use.

1. Install Ollama from [https://ollama.com](https://ollama.com)
2. Pull a model:
   ```bash
   ollama pull llama3       # or mistral, phi3, qwen2, gemma2
   ```
3. In `settings.yaml`:
   ```yaml
   chatbot:
     provider: ollama
   providers:
     ollama:
       base_url: http://localhost:11434
       model: llama3
   ```

</details>

<details>
<summary><strong>🟣 OpenAI (GPT-4 / GPT-3.5)</strong></summary>

1. Get your API key at [https://platform.openai.com](https://platform.openai.com)
2. Uncomment `openai` in `requirements.txt` and run `pip install openai`
3. In `settings.yaml`:
   ```yaml
   chatbot:
     provider: openai
   providers:
     openai:
       api_key: YOUR_OPENAI_API_KEY
       model: gpt-4o-mini
   ```

</details>

<details>
<summary><strong>🔵 Anthropic Claude</strong></summary>

1. Get your API key at [https://console.anthropic.com](https://console.anthropic.com)
2. Uncomment `anthropic` in `requirements.txt` and run `pip install anthropic`
3. In `settings.yaml`:
   ```yaml
   chatbot:
     provider: anthropic
   providers:
     anthropic:
       api_key: YOUR_ANTHROPIC_API_KEY
       model: claude-3-haiku-20240307
   ```

</details>

<details>
<summary><strong>🟡 IBM Watson Assistant</strong></summary>

1. Create a free IBM Cloud account at [https://cloud.ibm.com/registration](https://cloud.ibm.com/registration)
2. Provision Watson Assistant at [https://cloud.ibm.com/catalog/services/watson-assistant](https://cloud.ibm.com/catalog/services/watson-assistant)
3. Create an assistant, note your `API key`, `Service URL`, and `Assistant ID`
4. Uncomment `ibm-watson` in `requirements.txt` and install
5. In `settings.yaml`:
   ```yaml
   chatbot:
     provider: ibm_watson
   providers:
     ibm_watson:
       api_key: YOUR_IBM_API_KEY
       service_url: https://api.us-south.assistant.watson.cloud.ibm.com
       assistant_id: YOUR_ASSISTANT_ID
   ```

</details>

<details>
<summary><strong>🟢 Google Dialogflow ES</strong></summary>

1. Create a GCP project at [https://console.cloud.google.com](https://console.cloud.google.com)
2. Enable the Dialogflow API
3. Create a service account and download the JSON credentials file
4. Place it at `config/google-credentials.json`
5. In `settings.yaml`:
   ```yaml
   chatbot:
     provider: dialogflow
   providers:
     dialogflow:
       project_id: your-gcp-project-id
       credentials_path: config/google-credentials.json
   ```

</details>

<details>
<summary><strong>🟠 AWS Lex V2</strong></summary>

1. Log in to the AWS Console and open Lex V2
2. Create a bot, note the `Bot ID`, `Bot Alias ID`, and region
3. Create an IAM user with Lex permissions, note Access Key + Secret Key
4. In `settings.yaml`:
   ```yaml
   chatbot:
     provider: aws_lex
   providers:
     aws_lex:
       region: us-east-1
       access_key: YOUR_ACCESS_KEY
       secret_key: YOUR_SECRET_KEY
       bot_id: YOUR_BOT_ID
       bot_alias_id: YOUR_BOT_ALIAS_ID
   ```

</details>

---

## 📧 Email Notifications Setup

When a customer uses a trigger word (book, complaint, refund, etc.), the chatbot can email the business owner automatically. Works with any SMTP provider.

### Gmail Setup

1. Go to [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**
3. Go to **App Passwords** → Select Mail → Custom device name → Generate
4. Copy the 16-character app password into `settings.yaml`:

```yaml
email:
  enabled: true
  smtp_host: smtp.gmail.com
  smtp_port: 587
  sender: your-email@gmail.com
  app_password: xxxx xxxx xxxx xxxx
  recipient: owner@yourbusiness.com
```

> Works with Outlook (`smtp.office365.com:587`), AWS SES, and SendGrid SMTP too.

---

## ⚙️ Customisation

Edit `config/settings.yaml` to personalise for any business:

```yaml
chatbot:
  business_name: "Green Valley Clinic"
  bot_name: "Medi"
  welcome_message: "Hello! I'm Medi, your health centre assistant. How can I help?"
  email_trigger_keywords:
    - book
    - appointment
    - urgent
    - callback
  system_prompt: |
    You are a friendly assistant for Green Valley Clinic. Help patients
    book appointments, answer questions about services, and escalate
    urgent medical concerns to staff immediately.
```

---

## ☁️ Deployment — How This Differs From IBM Watson

> The original IBM Watson chatbot is **fully cloud-hosted on IBM's platform** — no server to run, it lives inside Watson Assistant's dashboard. This project is a **self-hosted Flask app** giving you full control and provider flexibility.

| | IBM Watson (original) | This project |
|---|---|---|
| Hosting | IBM Cloud (managed) | Your own server / Docker |
| Provider lock-in | IBM only | 6 providers, swap anytime |
| Cost | Free tier → paid | Depends on chosen provider |
| Local/private option | ❌ | ✅ via Ollama |
| Custom UI | Limited | Full custom HTML/CSS |

---

## 🐳 Docker Deployment

The easiest way to run the chatbot in any environment — no Python setup needed.

### Option A — Docker Compose (recommended)

```bash
# 1. Edit config/settings.yaml with your provider + credentials
# 2. Build and run
docker-compose up --build

# Stop
docker-compose down
```

To also run **Ollama locally** alongside the chatbot, uncomment the `ollama` service block in `docker-compose.yml`.

### Option B — Plain Docker

```bash
# Build
docker build -t ai-customer-chatbot .

# Run
docker run -p 5000:5000 \
  -v $(pwd)/config/settings.yaml:/app/config/settings.yaml \
  -v $(pwd)/logs:/app/logs \
  ai-customer-chatbot
```

Open `http://localhost:5000` ✅

---

## 🌐 Other Deployment Options

| Platform | Steps |
|---|---|
| **Local (no Docker)** | `pip install -r requirements.txt && python backend/app.py` |
| **Heroku** | `heroku create && git push heroku main` |
| **Railway / Render** | Connect repo → set start command to `gunicorn --bind 0.0.0.0:5000 backend.app:app` |
| **AWS EC2 / GCP VM** | Clone repo, install deps, run with `gunicorn` behind nginx |
| **Fly.io** | `fly launch` (auto-detects Dockerfile) |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## 📄 License

[MIT](LICENSE)
