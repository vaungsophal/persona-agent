# PO Agent — AI Twin for Your Portfolio

An agentic AI assistant that represents you to recruiters, clients, and fellow developers visiting your portfolio. Built with real tools, live data, and Telegram-powered lead capture.

## Architecture

```
Visitor ──► Vue 3 Chat Widget
                  │
                  ▼ FastAPI + Claude (Bedrock)
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
  Content     GitHub      Telegram
  Layer       API         Bot
  (local)     (live)      (action)
```

- **Content Layer** — structured Markdown/JSON files in `backend/content/` (bio, projects, skills, experience). Git-tracked source of truth.
- **Agent Loop** — Claude via AWS Bedrock (Singapore) with tool-calling. No vector DB needed since the corpus fits in context.
- **Live Tools** — `get_github_activity()` fetches real recent commits; `contact_po()` sends Telegram notifications.
- **Memory** — Session-level visitor detection (recruiter / client / dev) adapts response depth.
- **Guardrails** — Strict rules against fabrication, commitments, or impersonation. Unknown questions route to `contact_po`.

## Project Structure

```
po-agent/
├── backend/
│   ├── main.py            # FastAPI app + chat/contact endpoints
│   ├── agent.py           # Bedrock client + Claude tool-loop
│   ├── config.py          # Settings via env vars
│   ├── models.py          # Pydantic request/response schemas
│   ├── content/           # Portfolio content files
│   │   ├── bio.md
│   │   ├── projects/
│   │   ├── skills.json
│   │   ├── experience.json
│   │   └── certifications.json
│   ├── prompts/
│   │   └── system.md      # Persona + guardrails prompt
│   └── tools/
│       ├── search.py      # search_projects, get_project_details
│       ├── github.py      # get_github_activity (live API)
│       └── contact.py     # contact_po (Telegram notification)
├── frontend/
│   └── src/
│       ├── App.vue             # Floating chat widget root
│       ├── stores/chat.ts      # Pinia store
│       └── components/
│           ├── ChatWidget.vue
│           ├── ChatMessage.vue
│           └── ChatInput.vue
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # fill in your credentials
uvicorn main:app --reload
```

Required env vars (see `.env.example`):
- `AWS_REGION` — must be Bedrock-available region (e.g. `ap-southeast-1`)
- `BEDROCK_MODEL_ID` — Claude model ID
- `TELEGRAM_BOT_TOKEN` — bot token for contact notifications
- `TELEGRAM_CHAT_ID` — your chat ID for receiving messages

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE=http://localhost:8000` in `.env` for local dev.

### 3. Docker

```bash
docker compose up --build
```

### 4. Deploy to Cloud Run

```bash
# Build and push backend
docker build -f docker/Dockerfile.backend -t gcr.io/$PROJECT/po-agent-backend .
docker push gcr.io/$PROJECT/po-agent-backend
gcloud run deploy po-agent-backend --image gcr.io/$PROJECT/po-agent-backend

# Build and serve frontend from Cloud Storage or Cloud Run
docker build -f docker/Dockerfile.frontend -t gcr.io/$PROJECT/po-agent-frontend .
docker push gcr.io/$PROJECT/po-agent-frontend
gcloud run deploy po-agent-frontend --image gcr.io/$PROJECT/po-agent-frontend
```

## Tools

| Tool | Source | Description |
|------|--------|-------------|
| `search_projects(query)` | Local content | Search projects by keyword |
| `get_project_details(name)` | Local content | Full project details |
| `get_github_activity()` | GitHub API (live) | Recent public events |
| `contact_po(name, msg, info)` | Telegram Bot API | Send notification to Vaungsophal |

## Guardrails

The agent will never:
- Fabricate projects, credentials, or salary figures
- Accept job offers or make commitments on your behalf
- Impersonate anyone else

When asked something outside its knowledge, it offers to pass the question along via `contact_po`.

## Tech Stack

- **Frontend:** Vue 3, Pinia, Tailwind CSS, shadcn-vue
- **Backend:** Python, FastAPI, AWS Bedrock (Claude)
- **Infra:** Docker, Cloud Run, Telegram Bot API
