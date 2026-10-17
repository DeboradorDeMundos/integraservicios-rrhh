# src/agent_tools.py
"""Herramientas LangChain del agente IntegraBot (consulta, escritura, memoria)."""
from __future__ import annotations

import json
from contextvars import ContextVar
from typing import Any

from langchain_core.tools import tool

from src.config import SourceType
from src.memory import CaseMemoryStore
from src.rag_engine import format_docs
from src.retriever import get_retriever
from src.tickets import HRTicketClient

_session_id: ContextVar[str] = ContextVar("integrabot_session_id", default="default")
_profile: ContextVar[dict[str, str]] = ContextVar("integrabot_profile", default={})
_memory_store = CaseMemoryStore()
_ticket_client = HRTicketClient()
_last_docs: ContextVar[list] = ContextVar("integrabot_last_docs", default=[])


def set_agent_context(session_id: str, profile: dict[str, str] | None = None) -> None:
    _session_id.set(session_id)
    _profile.set(profile or {})
    _last_docs.set([])


def consume_retrieved_docs() -> list:
    docs = list(_last_docs.get() or [])
    _last_docs.set([])
    return docs


def _merge_docs(new_docs: list) -> None:
    current = list(_last_docs.get() or [])
    seen = {d.page_content[:80] for d in current}
    for doc in new_docs:
        key = doc.page_content[:80]
        if key not in seen:
            current.append(doc)
            seen.add(key)
    _last_docs.set(current)


@tool
def buscar_politicas_internas(consulta: str) -> str:
    """Consulta RIOHS y Contrato Colectivo (corpus interno)."""
    retriever = get_retriever(SourceType.INTERNAL)
    docs = retriever.invoke(consulta)
    _merge_docs(docs)
    body = format_docs(docs) if docs else "Sin fragmentos internos para esta consulta."
    return body[:6000]


@tool
def buscar_normativa_externa(consulta: str) -> str:
    """Consulta Código del Trabajo / Ley Karin (corpus externo)."""
    retriever = get_retriever(SourceType.EXTERNAL)
    docs = retriever.invoke(consulta)
    _merge_docs(docs)
    body = format_docs(docs) if docs else "Sin fragmentos externos para esta consulta."
    return body[:6000]


@tool
def guardar_memoria_caso(resumen: str, tema: str = "general") -> str:
    """Persiste un hecho o resumen en la memoria de largo plazo del caso."""
    memory = _memory_store.append_fact(_session_id.get(), resumen, tema=tema)
    return json.dumps(
        {"ok": True, "tema": memory.tema, "facts": len(memory.facts)},
        ensure_ascii=False,
    )


@tool
def registrar_ticket_gestion_personas(
    asunto: str,
    descripcion: str,
    categoria: str = "otro",
    prioridad: str = "media",
    confirmado_usuario: bool = False,
) -> str:
    """Registra ticket RRHH. categoria: beneficios|permisos|reglamento|ley_karin|otro."""
    if isinstance(confirmado_usuario, str):
        confirmado_usuario = confirmado_usuario.strip().lower() in {
            "true",
            "1",
            "si",
            "sí",
            "yes",
            "ok",
        }
    profile = _profile.get() or {}
    plan_sensitive = "sensible" in (descripcion or "").lower() or "sensible" in (asunto or "").lower()
    if not confirmado_usuario and not plan_sensitive:
        return (
            "NO_REGISTRADO: el colaborador no confirmó. "
            "Resume el caso y pregunta si desea abrir ticket en Gestión de Personas."
        )
    ticket = _ticket_client.create(
        asunto=asunto,
        descripcion=descripcion,
        categoria=categoria,
        prioridad=prioridad,
        colaborador=profile.get("nombre", ""),
        rut=profile.get("rut", ""),
    )
    _memory_store.register_ticket(_session_id.get(), ticket.id)
    _memory_store.append_fact(
        _session_id.get(),
        f"Ticket {ticket.id}: {ticket.asunto}",
        tema=categoria,
    )
    return json.dumps({"ok": True, "ticket": ticket.to_public_dict()}, ensure_ascii=False)


AGENT_TOOLS = [
    buscar_politicas_internas,
    buscar_normativa_externa,
    guardar_memoria_caso,
    registrar_ticket_gestion_personas,
]
TOOL_MAP = {t.name: t for t in AGENT_TOOLS}
