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
from langchain_core.runnables import RunnableLambda

from src.config import CORPUS_LABELS, SourceType
from src.conversation import format_chat_history
from src.guardrails import apply_response_guardrails
from src.local_generator import generate_local_answer
from src.models import create_llm, provider_label, uses_local_generator
from src.prompts import SYSTEM_PROMPT
from src.retriever import get_retriever

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
        return self.answer_with_docs(question, retrieved_docs, chat_history)

    def answer_with_docs(
        self,
        question: str,
        retrieved_docs: list,
        chat_history: str = "",
    ) -> tuple[str, list]:
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
    """Inicializa ChromaDB y la cadena de generación según MODEL_PROVIDER."""
    print(f"Proveedor activo: {provider_label()}")
    retriever = get_retriever()

    if uses_local_generator():
        generation_chain = RunnableLambda(
            lambda inputs: generate_local_answer(
                inputs["context"],
                inputs["question"],
                inputs.get("chat_history", ""),
            )
        )
    else:
        llm = create_llm()
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
