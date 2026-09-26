# Automotive Agent RAG

An AI customer-service agent for automotive manuals. Ask a question in
plain language ("When will the alarm be triggered?") and get an answer
grounded in the vehicle's manual — with an **Evidence** view showing the
exact manual, page, and text the answer came from.

## Architecture

- **Frontend**: React + Tailwind CSS (Vite) — `frontend/`
- **Backend**: FastAPI REST API — `backend/`
- **LLM orchestration**: LangChain tool-calling agent (Groq / Google Gemini / OpenAI)
- **Vector search**: FAISS, with local (no-API-key) embeddings via FastEmbed
- **Manual storage**: MongoDB (metadata + GridFS file storage), so uploaded
  and preloaded manuals persist and are listed back to you on your next
  visit. If MongoDB isn't reachable, the backend automatically falls back
  to an equivalent on-disk store so the app still works — `GET /api/health`
  reports which storage backend is active.

The previous Streamlit UI has been fully replaced by the React frontend
talking to the FastAPI backend over HTTP.

## Features

- Chat with an AI agent about a specific vehicle's manual (brand/model/year),
  with vehicle presets for 6 brands (Volkswagen, Toyota, Honda, Ford, BMW, Audi)
  plus free-text entry for anything else.
- Upload your own PDF manuals, or one-click load 4 bundled sample manuals
  (Volkswagen Taos, Toyota Camry, Honda Civic, Ford F-150 — all 2023).
- Click any registered vehicle chip to instantly set it as the active target
  vehicle.
- **Evidence panel**: every answer can show the retrieved manual excerpts,
  each with the source manual, page number, a relevance score, and a link to
  open the original PDF at that page.
- **Manual Store viewer** (the "DB" button): shows the live storage backend
  (MongoDB vs. local fallback) and every stored manual document — useful for
  demonstrating the MongoDB integration.
- Switch between Groq, Google Gemini, and OpenAI models at runtime.
- Light/dark theme toggle (persisted across visits).
- Copy-to-clipboard and regenerate-answer on any response, message
  timestamps, an autosizing chat input.
- Reset the knowledge base from the UI.

## A note on LLM API keys

This app calls Groq, Google Gemini, and OpenAI's own APIs — it cannot create
accounts or API keys with those providers on your behalf; you need to sign
up (Groq and Google AI Studio both have generous free tiers) and paste the
key into `backend/.env`. Without a key, that provider shows "no API key" in
the dropdown and returns a clear error if selected — it will not silently
fail. If a specific *model* errors after you send a prompt (e.g. "model not
found/decommissioned"), it means that model isn't enabled on your provider
account; pick a different one from the dropdown — the error message will
say so explicitly.

## Getting started

### 1. Backend

```sh
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in at least one LLM API key + MONGODB_URI
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. See `backend/.env.example` for
all configuration options.

### 2. Frontend

```sh
cd frontend
npm install
cp .env.example .env   # points VITE_API_BASE_URL at the backend
npm run dev
```

Open `http://localhost:5173`.

### 3. MongoDB

Point `MONGODB_URI` in `backend/.env` at a local `mongod` (default
`mongodb://localhost:27017`) or a MongoDB Atlas connection string. No
manual database/collection setup is required — they're created on first
use. Without MongoDB configured/reachable, manual metadata and files are
stored on disk under `backend/app/data/local_fallback_db/` instead.

## Project structure

```
backend/
  app/
    main.py          FastAPI app & routes
    agent.py         LLM providers + LangChain tool-calling agent
    db_mongo.py       MongoDB (+ local fallback) manual storage
    vector_store.py  FAISS index management
    pdf_utils.py     Per-page PDF extraction & chunking (for evidence)
    embeddings.py    FastEmbed embeddings with offline fallback
    data/manuals/    Bundled sample manual PDFs
  scripts/generate_manuals.py   Regenerates the bundled sample manuals
frontend/
  src/
    App.jsx                 App shell & state
    components/Sidebar.jsx        Control panel (provider, vehicle, manuals)
    components/ChatWindow.jsx     Chat UI
    components/EvidenceDrawer.jsx Evidence/source viewer
    api/client.js            Backend API client
```

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
