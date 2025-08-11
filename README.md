# Prompt Optimizer — Web App

A lightweight Flask web app that helps users craft clearer, more effective prompts for AI tools (ChatGPT, Claude, Gemini, etc.). It offers a **Quick** mode for one‑shot optimization and an **Interactive** mode that guides users through a few questions to build a high‑quality final prompt.

---

## Features

* **Quick mode:** Paste an idea, pick a tone (Standard / Technical / Informal or Custom), and get an optimized prompt with one‑click **Copy**.
* **Interactive mode:** Answer guided questions → receive tailored follow‑ups → get a final optimized prompt (with **Copy**).
* **Privacy page:** Clear, minimal policy (no account; no PII stored beyond what’s needed to generate the result).
* **Feedback link:** Optional post‑result form so users can share quick feedback.
* **Chrome extension link:** Homepage promotes the companion browser extension.

## Tech stack

* **Backend:** Flask, flask‑cors
* **AI layer:** Agno agent + Groq model (e.g., `qwen/qwen3-32b`) calling an external MCP server over SSE
* **Frontend:** Jinja templates, Bootstrap‑style UI
* **Process manager (deploy):** gunicorn

## Directory layout (example)

```
augustosouza8-prompt-optimizer-web-app/
├── README.md
├── LICENSE
├── requirements.txt
├── run.py
└── app/
    ├── __init__.py
    ├── agno_agent.py
    ├── routes.py
    └── templates/
        ├── base.html
        ├── index.html
        ├── quick.html
        ├── interactive_step1.html
        ├── interactive_step2.html
        ├── interactive_result.html
        └── privacy.html
```

## Requirements

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Key libraries: `Flask`, `flask-cors`, `agno`, `groq`, `mcp`, `gunicorn`.

## Configuration

Create a `.env` file (or set environment variables):

```bash
# Required for the agent/model call
GROQ_API_KEY=your_key_here

# Optional
SECRET_KEY=change_me
PORT=8000
```

* The MCP SSE endpoint is configured in `app/agno_agent.py` (look for the `_SSE_URL`). Update it if you host your own MCP server.

## Run locally

```bash
python run.py
# App binds 0.0.0.0 and uses PORT (default 8000)
```

Open: `http://localhost:8000/`

Common routes:

* **Home:** `/`
* **Quick:** `/quick`
* **Interactive:** `/interactive` → follow‑ups → result
* **Privacy:** `/privacy`

## Deploy

With Gunicorn (e.g., Render/Heroku‑style):

```bash
gunicorn run:app --bind 0.0.0.0:${PORT:-8000}
```

## How it works (high level)

1. The UI posts user input to Flask.
2. The server calls `query_agent(...)`, which uses **Agno** with **Groq** (e.g., `qwen/qwen3-32b`) and an **MCP** tool over SSE to produce the optimized prompt.
3. The result is rendered back to the page with a **Copy** helper.

## Privacy

* No accounts. No PII storage. Prompts are sent only to generate the optimized result. Session cookies are temporary. See `templates/privacy.html`.

## License

MIT — see `LICENSE`.
