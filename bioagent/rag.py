"""
BioAgent — Motor RAG ligero (sin ChromaDB)
Usa sentence-transformers + numpy para búsqueda semántica en memoria.
Compatible con Python 3.14+, sin conflictos de pydantic.
"""
import asyncio
import logging
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
from github import Github, GithubException
from sentence_transformers import SentenceTransformer

from bioagent.config import (
    GITHUB_TOKEN,
    GITHUB_REPO,
    KNOWLEDGE_DIR,
    CHROMA_PERSIST_DIR,  # reutilizamos como directorio de caché
)

logger = logging.getLogger(__name__)

# ── Constantes ────────────────────────────────────────────────────────────────
EMBED_MODEL = "all-MiniLM-L6-v2"
CACHE_FILE = Path(CHROMA_PERSIST_DIR) / "rag_index.pkl"
CHUNK_SIZE = 600   # palabras por chunk
CHUNK_OVERLAP = 80

# ── Estado del índice en memoria ──────────────────────────────────────────────
_model: Optional[SentenceTransformer] = None
_chunks: list[str] = []
_sources: list[str] = []
_embeddings: Optional[np.ndarray] = None
_indexed = False


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("🤖 Cargando modelo de embeddings (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer(EMBED_MODEL)
        logger.info("✅ Modelo de embeddings cargado.")
    return _model


def _chunk_text(text: str, source: str) -> tuple[list[str], list[str]]:
    """Divide texto en chunks con overlap."""
    words = text.split()
    chunks, sources = [], []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i: i + CHUNK_SIZE])
        chunks.append(chunk)
        sources.append(source)
        i += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks, sources


def _cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Similitud coseno entre query y todos los embeddings."""
    norms = np.linalg.norm(matrix, axis=1)
    norms[norms == 0] = 1e-10
    query_norm = np.linalg.norm(query_vec)
    if query_norm == 0:
        query_norm = 1e-10
    return (matrix @ query_vec) / (norms * query_norm)


def build_index() -> int:
    """
    Descarga archivos .md de GitHub, genera embeddings y guarda caché local.
    Retorna número de chunks indexados.
    """
    global _chunks, _sources, _embeddings, _indexed

    # Intentar cargar caché primero
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "rb") as f:
                data = pickle.load(f)
            _chunks = data["chunks"]
            _sources = data["sources"]
            _embeddings = data["embeddings"]
            _indexed = True
            logger.info(f"✅ RAG: {len(_chunks)} chunks cargados desde caché.")
            return len(_chunks)
        except Exception as e:
            logger.warning(f"⚠️ Caché corrupta, re-indexando: {e}")

    if not GITHUB_TOKEN:
        logger.warning("⚠️ RAG: GITHUB_TOKEN no configurado.")
        return 0

    logger.info(f"🔄 RAG: Descargando de {GITHUB_REPO}/{KNOWLEDGE_DIR}...")

    try:
        gh = Github(GITHUB_TOKEN)
        repo = gh.get_repo(GITHUB_REPO)
        contents = repo.get_contents(KNOWLEDGE_DIR)

        all_chunks: list[str] = []
        all_sources: list[str] = []

        for file in contents:
            if not file.name.endswith(".md"):
                continue
            logger.info(f"  📄 {file.name} ({file.size:,} bytes)")
            text = file.decoded_content.decode("utf-8")
            c, s = _chunk_text(text, file.name)
            all_chunks.extend(c)
            all_sources.extend(s)

        if not all_chunks:
            logger.warning("⚠️ RAG: No se encontraron archivos .md.")
            return 0

        # Generar embeddings
        logger.info(f"⚙️ RAG: Generando embeddings para {len(all_chunks)} chunks...")
        model = _get_model()
        embeddings = model.encode(all_chunks, show_progress_bar=True, batch_size=32)

        _chunks = all_chunks
        _sources = all_sources
        _embeddings = embeddings
        _indexed = True

        # Guardar caché
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "wb") as f:
            pickle.dump({"chunks": _chunks, "sources": _sources, "embeddings": _embeddings}, f)

        logger.info(f"✅ RAG: {len(_chunks)} chunks indexados y guardados en caché.")
        return len(_chunks)

    except GithubException as e:
        logger.error(f"❌ RAG GitHub error: {e}")
        return 0
    except Exception as e:
        logger.error(f"❌ RAG error: {e}", exc_info=True)
        return 0


def search(query: str, n_results: int = 4) -> str:
    """
    Busca los N chunks más relevantes para la query.
    Retorna string formateado para inyectar en el prompt de Gemini.
    """
    if not _indexed or _embeddings is None or len(_chunks) == 0:
        return ""

    try:
        model = _get_model()
        query_vec = model.encode([query])[0]
        scores = _cosine_similarity(query_vec, _embeddings)

        top_indices = np.argsort(scores)[::-1][:n_results]

        context_parts = []
        for idx in top_indices:
            if scores[idx] < 0.25:  # umbral mínimo de relevancia
                continue
            source = _sources[idx]
            context_parts.append(f"[{source}]\n{_chunks[idx]}")

        if not context_parts:
            return ""

        context = "\n\n---\n\n".join(context_parts)
        return f"## Información relevante del Dr. La Rosa:\n\n{context}\n\n---"

    except Exception as e:
        logger.error(f"❌ RAG search error: {e}")
        return ""


async def build_index_async() -> int:
    """Versión async de build_index para no bloquear el event loop."""
    return await asyncio.to_thread(build_index)
