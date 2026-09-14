# src/rag_engine.py
"""
Pipeline RAG dual de IntegraBot (criterios IE3 e IE4).

Módulos desacoplados:
- config.py      → caso organizacional y parámetros
- ingestion.py   → carga, etiquetado interno/externo, ChromaDB
- prompts.py     → System Prompt (IE2)
- guardrails.py  → validación post-respuesta (IE2)
- conversation.py→ historial acotado (IE4)
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from src.config import (
    CORPUS_LABELS,
    EMBEDDING_MODEL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    RETRIEVER_K,
    RETRIEVER_LAMBDA,
    SourceType,
)
from src.conversation import format_chat_history
from src.guardrails import apply_response_guardrails
from src.ingestion import build_vectorstore
from src.prompts import SYSTEM_PROMPT

load_dotenv()


def format_docs(docs) -> str:
    """
    Concatena fragmentos recuperados con trazabilidad IE3:
    nombre, página y tipo de corpus (interno / externo).
    """
    formatted = []
    for doc in docs:
        source_name = os.path.basename(doc.metadata.get("source", "Documento"))
        page = doc.metadata.get("page", 0) + 1
        source_type = doc.metadata.get("source_type", SourceType.INTERNAL.value)
        label = CORPUS_LABELS.get(
            SourceType(source_type),
            "Documento corporativo",
        )
        formatted.append(
            f"--- Fuente: {source_name} (Pág. {page}) [{source_type}] ---\n"
            f"Tipo: {label}\n"
            f"{doc.page_content}"
        )
    return "\n\n".join(formatted)


@dataclass
class RAGPipeline:
    """Orquestador IE4: recuperación → generación → guardrails."""

    retriever: object
    generation_chain: object

    def query(self, question: str, chat_history: str = "") -> tuple[str, list]:
        """
        Ejecuta una consulta completa.

        Returns:
            tuple[str, list]: respuesta final y documentos recuperados (MMR k=4).
        """
        retrieved_docs = self.retriever.invoke(question)
        context = format_docs(retrieved_docs)
        history = chat_history or "Sin conversación previa."
        raw_answer = self.generation_chain.invoke(
            {
                "context": context,
                "question": question,
                "chat_history": history,
            }
        )
        answer = apply_response_guardrails(raw_answer)
        return answer, retrieved_docs


def initialize_rag_system() -> RAGPipeline:
    """
    Inicializa ChromaDB y la cadena de generación con Google Gemini 2.5 Flash.
    """
    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError(
            "Falta GOOGLE_API_KEY. Copia .env.example a .env y coloca tu clave de Google AI Studio."
        )

    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = build_vectorstore(embeddings)

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": RETRIEVER_K, "lambda_mult": RETRIEVER_LAMBDA},
    )

    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    generation_chain = SYSTEM_PROMPT | llm | StrOutputParser()

    return RAGPipeline(retriever=retriever, generation_chain=generation_chain)


def get_rag_chain():
    """
    Punto de entrada usado por la interfaz Streamlit.

    Returns:
        RAGPipeline con método .query(question, chat_history).
    """
    return initialize_rag_system()


__all__ = [
    "RAGPipeline",
    "format_chat_history",
    "format_docs",
    "get_rag_chain",
    "initialize_rag_system",
]
