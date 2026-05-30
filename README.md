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
├── requirements.txt
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

## Supported cities

Delhi, Mumbai, Goa, Bangalore, Chennai, Hyderabad, Kolkata, Jaipur
