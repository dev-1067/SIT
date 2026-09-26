"""Embeddings backend with a resilient offline fallback.

Primary path: FastEmbed (local ONNX models, no API key required). FastEmbed
downloads its model weights from Hugging Face the first time it runs, so if
the machine has no internet access (or HF is unreachable) we transparently
fall back to a deterministic hashing-based embedding instead of crashing the
whole app. This keeps indexing/search always available.
"""
import hashlib
import logging
from functools import lru_cache
from typing import List

from langchain_core.embeddings import Embeddings

logger = logging.getLogger("automotive_rag.embeddings")

HASH_EMBEDDING_DIM = 384


class OfflineHashEmbeddings(Embeddings):
    """Deterministic, dependency-free embeddings used as a fallback.

    Uses a hashing trick over word tokens so semantically similar text
    (sharing words) still lands close together in vector space. Not as
    strong as a trained model, but keeps the app fully functional when the
    real embeddings model cannot be downloaded.
    """

    def __init__(self, dim: int = HASH_EMBEDDING_DIM):
        self.dim = dim

    def _embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        tokens = text.lower().split()
        if not tokens:
            return vec
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % self.dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vec[idx] += sign
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)


@lru_cache(maxsize=1)
def get_embeddings() -> Embeddings:
    try:
        from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

        embeddings = FastEmbedEmbeddings()
        # Force a lazy model download/init to happen now so failures surface here.
        embeddings.embed_query("healthcheck")
        logger.info("Using FastEmbed local embeddings.")
        return embeddings
    except Exception as exc:  # noqa: BLE001 - broad on purpose, this is a fallback path
        logger.warning(
            "FastEmbed embeddings unavailable (%s). Falling back to offline hashing embeddings.",
            exc,
        )
        return OfflineHashEmbeddings()
