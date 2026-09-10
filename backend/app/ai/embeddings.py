import hashlib
import logging
import math
import re
from functools import lru_cache

import numpy as np

from app.config.settings import settings

logger = logging.getLogger(__name__)
_DIM = 384
_TOKEN = re.compile(r"[a-z0-9+#.]+")


@lru_cache(maxsize=1)
def _load_model():
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(settings.embedding_model)
    except Exception as exc:  # model download or import failure
        logger.warning("Falling back to hashed embeddings: %s", exc)
        return None


def _hashed_embedding(text: str) -> np.ndarray:
    vec = np.zeros(_DIM, dtype=np.float32)
    for tok in _TOKEN.findall(text.lower()):
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        vec[h % _DIM] += 1.0 if (h >> 8) % 2 else -1.0
    norm = float(np.linalg.norm(vec))
    return vec / norm if norm else vec


def embed_text(text: str) -> list[float]:
    model = _load_model()
    if model is None:
        return _hashed_embedding(text).tolist()
    return model.encode(text[:5000], normalize_embeddings=True).tolist()


def cosine_similarity(a: list[float] | None, b: list[float] | None) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0
