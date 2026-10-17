# src/retriever.py
"""Acceso compartido a ChromaDB y retrievers filtrados por corpus (IE4)."""
from __future__ import annotations

from src.config import RETRIEVER_K, RETRIEVER_LAMBDA, SourceType
from src.ingestion import build_vectorstore
from src.models import create_embeddings

_cache: dict[str, object] = {}


def get_vectorstore():
    if "vectorstore" not in _cache:
        embeddings = create_embeddings()
        _cache["embeddings"] = embeddings
        _cache["vectorstore"] = build_vectorstore(embeddings)
    return _cache["vectorstore"]


def get_retriever(source_type: SourceType | None = None):
    vectorstore = get_vectorstore()
    search_kwargs: dict = {"k": RETRIEVER_K, "lambda_mult": RETRIEVER_LAMBDA}
    if source_type is not None:
        search_kwargs["filter"] = {"source_type": source_type.value}
    return vectorstore.as_retriever(search_type="mmr", search_kwargs=search_kwargs)


def reset_retriever_cache() -> None:
    _cache.clear()
