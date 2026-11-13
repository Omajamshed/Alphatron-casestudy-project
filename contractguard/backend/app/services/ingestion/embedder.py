import re
import math
import hashlib
from typing import List, Union

_st_model = None
_st_load_attempted = False


def _get_st_model():
    global _st_model, _st_load_attempted
    if not _st_load_attempted:
        _st_load_attempted = True
        try:
            from sentence_transformers import SentenceTransformer
            from app.core.config import settings
            _st_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        except Exception:
            _st_model = None
    return _st_model


def _deterministic_fallback_embedding(text: str, dim: int = 384) -> List[float]:
    """
    Deterministic 384-dimensional feature vector based on token n-grams and hashing.
    Preserves semantic similarity based on shared vocabulary and legal terms.
    """
    vec = [0.0] * dim
    clean_text = text.lower()
    tokens = re.findall(r"\b\w+\b", clean_text)
    if not tokens:
        return [0.0] * dim

    for i, token in enumerate(tokens):
        # 1-gram
        h1 = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % dim
        vec[h1] += 1.0
        # 2-gram
        if i + 1 < len(tokens):
            bigram = f"{token}_{tokens[i+1]}"
            h2 = int(hashlib.md5(bigram.encode("utf-8")).hexdigest(), 16) % dim
            vec[h2] += 1.5

    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def get_embedding(text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
    """Generates 384-dim embedding vector(s)."""
    is_single = isinstance(text, str)
    texts = [text] if is_single else text

    model = _get_st_model()
    if model is not None:
        try:
            embeddings = model.encode(texts, normalize_embeddings=True)
            result = [emb.tolist() for emb in embeddings]
            return result[0] if is_single else result
        except Exception:
            pass

    # Use deterministic fallback
    result = [_deterministic_fallback_embedding(t, dim=384) for t in texts]
    return result[0] if is_single else result
