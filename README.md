# PERSONA.IQ

An autonomous profiling agent that synthesizes structured digital identities from public web footprints (LinkedIn, GitHub, portfolios, and web search) using LangGraph, Groq, and Playwright.

---

## Architecture Flow

```mermaid
graph LR
    User[User Input] -->|Name + URLs| UI[Next.js 16 UI]
    UI -->|POST /build-profile| API[FastAPI Server]
    API -->|Background Task| Agent[LangGraph ReAct Loop]

    subgraph "Agentic Loop"
        Agent -->|1. Reason| R[Decide Action]
        R -->|2. Act| A[Scrape / Search / NER]
        A -->|3. Observe| O[Integrate Data]
        O -->|4. Reflect| Ref[Evaluate Limits & Completeness]
        Ref -->|Repeat / Finalize| Agent
    end

    Agent -->|Save Profile| DB[(PostgreSQL)]
    UI -.->|Poll /job/:id| API
```

---

## Tech Stack

- **Backend**: FastAPI, LangGraph, Groq (configurable via `GROQ_MODEL`, e.g. `qwen/qwen3.8-27b`), Playwright, Tavily Search, ChromaDB, SQLAlchemy, PostgreSQL.
- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, Zustand, Framer Motion.

---

## Project Structure

```
Agentic-AI/
├── backend/
│   ├── .env                     # API keys and database configuration
│   ├── requirements.txt         # Python dependencies
│   └── app/
│       ├── main.py              # FastAPI endpoints and background job runner
│       ├── agents/
│       │   └── orchestrator.py  # LangGraph state machine & reasoning logic
│       ├── db/
│       │   └── database.py      # SQLAlchemy models & connection
│       ├── models/
│       │   └── profile.py       # Pydantic data schemas
│       ├── services/            # Scraper, search, NER, memory services
│       └── utils/               # Job store and execution logger
└── frontend/
    ├── package.json             # Next.js and frontend dependencies
    └── src/
        ├── app/                 # Next.js pages and layouts
        ├── components/          # InputForm, AgentTimeline, ProfileDashboard
        ├── store/               # Zustand state store
        └── mockData.ts          # Simulation profile for offline testing
```

---

## Environment Setup

Create `backend/.env` with your API keys:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/persona_iq
GROQ_MODEL=qwen/qwen3.8-27b
```

*(If you haven't created the database in PostgreSQL yet, run `CREATE DATABASE persona_iq;`)*

---

## How to Run

### 1. Backend

```powershell
cd backend

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies and Playwright browser
pip install -r requirements.txt
playwright install chromium

# Start the API server
uvicorn app.main:app --reload --reload-dir app --port 8000
```

- API Base URL: `http://localhost:8000`
- API Documentation (Swagger): `http://localhost:8000/docs`

### 2. Frontend

Open a new terminal:

```powershell
cd frontend
npm install
npm run dev
```

- Web App: `http://localhost:3000`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/build-profile` | Accepts `{"name": "...", "urls": [...]}` and starts profile synthesis in background. |
| `GET` | `/job/{job_id}` | Returns job status (`running`, `completed`, `error`, `cancelled`) and execution steps. |
| `POST` | `/job/{job_id}/cancel` | Aborts a running profile generation job. |

---

## Testing / Demo

- **Live Profile**: Enter a target name and profile URLs in the dashboard and click **Generate Profile**.
- **Offline Simulation**: Click the **Simulate** button in the top-right header on `http://localhost:3000` to preview the agent timeline and dashboard without consuming API credits.
