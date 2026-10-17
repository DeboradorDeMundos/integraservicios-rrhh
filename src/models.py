# src/models.py
"""
Fabrica de embeddings y LLM segun MODEL_PROVIDER.

Proveedores:
- google  -> Gemini embeddings + Gemini Flash (requiere GOOGLE_API_KEY)
- groq    -> HuggingFace local + Groq LLM (requiere GROQ_API_KEY)
- local   -> HuggingFace local + generador extractivo (sin API, ideal para pruebas)
"""
from __future__ import annotations

import os

from src.config import (
    EMBEDDING_MODEL,
    GROQ_LLM_MODEL,
    HF_EMBEDDING_MODEL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    MODEL_PROVIDER,
)


def get_provider() -> str:
    """Lee MODEL_PROVIDER en cada llamada (permite fallback demo sin reiniciar)."""
    return os.getenv("MODEL_PROVIDER", MODEL_PROVIDER).strip().lower()


def create_embeddings():
    """Embeddings acordes al proveedor activo."""
    provider = get_provider()
    if provider == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        if not os.getenv("GOOGLE_API_KEY"):
            raise EnvironmentError(
                "Falta GOOGLE_API_KEY para MODEL_PROVIDER=google. "
                "Usa MODEL_PROVIDER=local o MODEL_PROVIDER=groq en .env."
            )
        return GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name=HF_EMBEDDING_MODEL)


def create_llm():
    """LLM de chat acordes al proveedor activo."""
    provider = get_provider()
    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        if not os.getenv("GOOGLE_API_KEY"):
            raise EnvironmentError(
                "Falta GOOGLE_API_KEY para MODEL_PROVIDER=google. "
                "Usa MODEL_PROVIDER=local o MODEL_PROVIDER=groq en .env."
            )
        return ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

    if provider == "groq":
        from langchain_groq import ChatGroq

        if not os.getenv("GROQ_API_KEY"):
            raise EnvironmentError(
                "Falta GROQ_API_KEY para MODEL_PROVIDER=groq. "
                "Obtén una clave gratis en https://console.groq.com "
                "o usa MODEL_PROVIDER=local en .env."
            )
        return ChatGroq(model=GROQ_LLM_MODEL, temperature=LLM_TEMPERATURE)

    raise EnvironmentError(f"Proveedor desconocido: {provider}")


def uses_local_generator() -> bool:
    return get_provider() == "local"


def provider_label() -> str:
    labels = {
        "google": f"Google Gemini ({LLM_MODEL})",
        "groq": f"Groq ({GROQ_LLM_MODEL})",
        "local": "Local extractivo (sin API)",
    }
    return labels.get(get_provider(), get_provider())
