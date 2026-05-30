# Yatra — AI Travel Planning Assistant

An agentic AI system that plans multi-day trips across Indian cities.
It autonomously selects flights, hotels, and attractions, fetches weather,
and produces a full budget breakdown.

## Project Structure

```
travel_agent/
├── data/
│   ├── flights.json
│   ├── hotels.json
│   └── places.json
├── tools.py          LangChain tools: flights, hotels, places, weather, budget
├── agent.py          LangChain agent + LLM loader (Anthropic or HuggingFace)
├── api_server.py     Flask REST API consumed by the frontend
├── app.py            Streamlit UI (standalone, no Flask needed)
├── index.html        HTML/JS frontend (talks to api_server.py)
├── requirements.txt
├── Procfile          For Render / Railway / Heroku
├── render.yaml       One-click Render deployment config
├── .env.example      Copy to .env and fill in your keys
└── .gitignore
```

## Setup (local)

```bash
git clone <your-repo>
cd travel_agent

pip install -r requirements.txt

cp .env.example .env
# Edit .env — add your HF_API_TOKEN or ANTHROPIC_API_KEY
```

---

## Testing without the frontend

### Option 1 — Command line (agent.py direct)

```bash
python agent.py "Plan a 3-day trip from Delhi to Goa"
```

### Option 2 — Python import

```python
from agent import run_agent
print(run_agent("Plan a 3-day trip from Delhi to Goa"))
```

### Option 3 — Streamlit UI (self-contained, no Flask)

```bash
streamlit run app.py
```
Opens at http://localhost:8501

### Option 4 — curl against the API server

Start the server:
```bash
python api_server.py
```

Health check:
```bash
curl http://localhost:5000/api/health
```

Plan a trip:
```bash
curl -X POST http://localhost:5000/api/plan \
  -H "Content-Type: application/json" \
  -d '{"query": "Plan a 3-day trip from Delhi to Goa with budget Rs.4000 per night"}'
```

---

## Hosting the backend for free — Render

1. Push this repo to GitHub.
2. Go to https://render.com and create a free account.
3. Click New > Web Service, connect your GitHub repo.
4. Render auto-detects render.yaml. Set the HF_API_TOKEN environment variable
   in the Render dashboard under Environment.
5. Deploy. Your API URL will be https://yatra-travel-api.onrender.com (or similar).

Note: Render free tier spins down after 15 minutes of inactivity.
The first request after sleep takes ~30 seconds to wake up.

---

## Hosting the frontend for free — Netlify

The frontend is a single static HTML file with no build step.

1. Go to https://netlify.com and create a free account.
2. Drag and drop index.html into the Netlify dashboard (or use Netlify Drop
   at https://app.netlify.com/drop).
3. Netlify gives you a public URL instantly, e.g. https://yatra-xyz.netlify.app.
4. Open index.html, update the default API URL in the input field to your
   Render backend URL, or set it at runtime via the API server URL field in the UI.

Alternatively, use GitHub Pages:
1. Push index.html to a public GitHub repo.
2. Go to Settings > Pages > Deploy from branch > main / root.
3. Your site is live at https://username.github.io/repo-name.

---

## Environment variables

| Variable          | Required for              | Default                              |
|-------------------|---------------------------|--------------------------------------|
| LLM_PROVIDER      | always                    | anthropic                            |
| HF_API_TOKEN      | LLM_PROVIDER=huggingface  | —                                    |
| HF_MODEL          | LLM_PROVIDER=huggingface  | mistralai/Mistral-7B-Instruct-v0.3   |
| ANTHROPIC_API_KEY | LLM_PROVIDER=anthropic    | —                                    |
| ANTHROPIC_MODEL   | LLM_PROVIDER=anthropic    | claude-sonnet-4-20250514             |
| PORT              | api_server.py             | 5000                                 |
| FLASK_DEBUG       | api_server.py             | false                                |
| ALLOWED_ORIGIN    | api_server.py (CORS)      | *                                    |

---

## API reference

### GET /api/health
Returns server status and the active LLM provider.

```json
{ "status": "ok", "provider": "huggingface" }
```

### POST /api/plan
Plans a trip from a natural language query.

Request:
```json
{ "query": "Plan a 3-day trip from Delhi to Goa" }
```

Response:
```json
{ "result": "TRIP SUMMARY\n============\n..." }
```

Error:
```json
{ "error": "HF_API_TOKEN is required when LLM_PROVIDER=huggingface." }
```

---

## Supported cities

Delhi, Mumbai, Goa, Bangalore, Chennai, Hyderabad, Kolkata, Jaipur
