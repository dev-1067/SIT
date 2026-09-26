import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MANUALS_DIR = DATA_DIR / "manuals"
FAISS_DIR = DATA_DIR / "local_db"
LOCAL_FALLBACK_DIR = DATA_DIR / "local_fallback_db"

MANUALS_DIR.mkdir(parents=True, exist_ok=True)
FAISS_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_FALLBACK_DIR.mkdir(parents=True, exist_ok=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017").strip()
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "automotive_rag").strip()

CORS_ORIGINS = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()
]

EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "BAAI/bge-small-en-v1.5")

# Bundled sample manuals that ship with the app so users have something to
# search immediately, before uploading their own manuals.
PRELOADED_MANUALS = {
    "vw_taos_2023": {
        "label": "Volkswagen Taos (2023)",
        "filename": "vw_taos_2023.pdf",
        "brand": "Volkswagen",
        "model": "Taos",
        "year": "2023",
    },
    "toyota_camry_2023": {
        "label": "Toyota Camry (2023)",
        "filename": "toyota_camry_2023.pdf",
        "brand": "Toyota",
        "model": "Camry",
        "year": "2023",
    },
    "honda_civic_2023": {
        "label": "Honda Civic (2023)",
        "filename": "honda_civic_2023.pdf",
        "brand": "Honda",
        "model": "Civic",
        "year": "2023",
    },
    "ford_f150_2023": {
        "label": "Ford F-150 (2023)",
        "filename": "ford_f150_2023.pdf",
        "brand": "Ford",
        "model": "F-150",
        "year": "2023",
    },
}
