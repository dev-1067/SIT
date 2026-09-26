import shutil
from typing import List, Optional, Tuple

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from .config import FAISS_DIR
from .embeddings import get_embeddings

_INDEX_FILE = FAISS_DIR / "index.faiss"


def index_exists() -> bool:
    return _INDEX_FILE.exists()


def load_index() -> Optional[FAISS]:
    if not index_exists():
        return None
    return FAISS.load_local(str(FAISS_DIR), get_embeddings(), allow_dangerous_deserialization=True)


def add_documents(documents: List[Document]) -> int:
    if not documents:
        return 0
    embeddings = get_embeddings()
    if index_exists():
        db = FAISS.load_local(str(FAISS_DIR), embeddings, allow_dangerous_deserialization=True)
        db.add_documents(documents)
    else:
        db = FAISS.from_documents(documents, embeddings)
    db.save_local(str(FAISS_DIR))
    return len(documents)


def get_retriever(k: int = 4):
    db = load_index()
    if db is None:
        return None
    return db.as_retriever(search_kwargs={"k": k})


def search_with_scores(query: str, k: int = 4) -> List[Tuple[Document, float]]:
    """Similarity search returning (document, relevance) pairs for evidence display.

    FAISS returns an L2 distance (lower = more similar); we convert it to a
    0-1 "relevance" score so the UI can show something intuitive.
    """
    db = load_index()
    if db is None:
        return []
    pairs = db.similarity_search_with_score(query, k=k)
    return [(doc, 1.0 / (1.0 + max(distance, 0.0))) for doc, distance in pairs]


def reset_index() -> None:
    if FAISS_DIR.exists():
        shutil.rmtree(FAISS_DIR)
    FAISS_DIR.mkdir(parents=True, exist_ok=True)
