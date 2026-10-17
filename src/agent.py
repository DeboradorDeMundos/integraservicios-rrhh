# src/agent.py
"""
Agente funcional EP2 — orquestación con herramientas LangChain.

- Consulta: tools RAG interno/externo
- Escritura: tickets RRHH + memoria de caso
- Razonamiento: plan explícito (planner) + bucle tool-calling (Gemini/Groq)
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from src.agent_prompts import AGENT_SYSTEM_PROMPT
from src.agent_tools import (
    AGENT_TOOLS,
    TOOL_MAP,
    consume_retrieved_docs,
    set_agent_context,
)
from src.config import AGENT_HISTORY_LIMIT, AGENT_MAX_TOOL_TURNS, SourceType
from src.conversation import format_chat_history
from src.memory import CaseMemoryStore
from src.models import create_llm, uses_local_generator
from src.planner import ExecutionPlan, TaskKind, plan_for_question
from src.prompts import DERIVATION_PHRASE, SENSITIVE_ESCALATION_REPLY
from src.rag_engine import get_rag_chain
from src.retriever import get_retriever
from src.tickets import HRTicketClient

_memory_store = CaseMemoryStore()
_ticket_client = HRTicketClient()
_logger = logging.getLogger("integrabot.agent")


def _is_rate_limit(exc: BaseException) -> bool:
    raw = f"{type(exc).__name__}: {exc}".lower()
    return any(
        token in raw
        for token in ("429", "quota", "resource_exhausted", "rate limit", "rate_limit")
    )


def _fallback_to_local_orchestration(
    plan: ExecutionPlan,
    question: str,
    chat_history: str,
    session_id: str,
    profile: dict[str, str] | None,
) -> AgentTurn:
    """Si Google/Groq agotó cuota, ejecuta el plan sin APIs de chat."""
    from src.retriever import reset_retriever_cache

    _logger.warning("Cuota/límite de IA — fallback a modo local (demo)")
    os.environ["MODEL_PROVIDER"] = "local"
    reset_retriever_cache()
    return _execute_orchestrated_plan(
        plan, question, chat_history, session_id, profile
    )


@dataclass
class AgentTurn:
    text: str
    sources: list[dict] = field(default_factory=list)
    tickets: list[dict] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    plan_lines: list[str] = field(default_factory=list)
    task_kind: str = ""


def _content_to_text(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))
        return "\n".join(parts).strip()
    return str(content).strip()


def _profile_text(profile: dict[str, str] | None) -> str:
    profile = profile or {}
    bits = []
    if profile.get("nombre"):
        bits.append(f"Nombre: {profile['nombre']}")
    if profile.get("rut"):
        bits.append(f"RUT: {profile['rut']}")
    if not bits:
        return "Sin nombre/RUT registrados. Solicítalos solo si hace falta para un ticket."
    return " · ".join(bits)


def _history_to_lc(history: list[dict[str, str]]) -> list:
    trimmed = history[-AGENT_HISTORY_LIMIT:]
    messages = []
    for item in trimmed:
        if item.get("role") == "user":
            messages.append(HumanMessage(content=item.get("content", "")))
        elif item.get("role") == "assistant" and item.get("content"):
            messages.append(AIMessage(content=item.get("content", "")))
    return messages


def _collect_sources(docs) -> list[dict]:
    import os

    return [
        {
            "name": os.path.basename(doc.metadata.get("source", "PDF")),
            "page": doc.metadata.get("page", 0) + 1,
            "content": doc.page_content,
            "source_type": doc.metadata.get("source_type", SourceType.INTERNAL.value),
        }
        for doc in docs
    ]


def _is_follow_up(history: list[dict[str, str]]) -> bool:
    return len([m for m in history if m.get("role") == "user"]) >= 1


def _asks_ticket_status(question: str) -> bool:
    q = question.lower()
    return any(
        token in q
        for token in (
            "ticket",
            "int-",
            "estado del",
            "estado de",
            "seguimiento",
            "abierto",
            "cerrado",
            "seguir",
        )
    )


def _orchestrated_follow_up(
    plan: ExecutionPlan,
    question: str,
    session_id: str,
) -> AgentTurn | None:
    """Seguimiento con memoria/tickets — sin RAG irrelevante en preguntas de ticket."""
    memory = _memory_store.load(session_id)
    tools_used: list[str] = ["recuperar_memoria_caso"]

    if _asks_ticket_status(question):
        tools_used.append("consultar_ticket_gestion_personas")
        if not memory.ticket_ids:
            return AgentTurn(
                text=(
                    "En la memoria de esta sesión no hay tickets registrados todavía. "
                    "Si acabas de abrir uno, repite la consulta sensible o indica el número INT."
                ),
                plan_lines=plan.as_lines(),
                task_kind=plan.kind.value,
                tools_used=tools_used,
            )
        public: list[dict] = []
        lines: list[str] = []
        for tid in memory.ticket_ids:
            ticket = _ticket_client.get(tid)
            if not ticket:
                lines.append(f"- **{tid}**: registrado en sesión; detalle no encontrado en el mock local.")
                continue
            public.append(ticket.to_public_dict())
            lines.append(
                f"- **{ticket.id}** · estado **{ticket.estado}** · {ticket.asunto} "
                f"(prioridad {ticket.prioridad}, categoría {ticket.categoria})."
            )
        text = (
            "Según la memoria de caso y el registro de Gestión de Personas:\n\n"
            + "\n".join(lines)
            + "\n\nUn ejecutivo de RRHH actualizará el estado cuando avance el trámite."
        )
        _memory_store.append_fact(session_id, f"Follow-up ticket: {question[:180]}", tema="seguimiento_caso")
        tools_used.append("guardar_memoria_caso")
        return AgentTurn(
            text=text,
            tickets=public,
            tools_used=tools_used,
            plan_lines=plan.as_lines(),
            task_kind=plan.kind.value,
        )

    if memory.facts or memory.ticket_ids or memory.tema:
        block = memory.to_prompt_block()
        text = (
            "Retomo el contexto de tu caso en esta sesión:\n\n"
            f"{block}\n\n"
            "Si necesitas una nueva búsqueda en reglamento o contrato, dime el tema concreto."
        )
        _memory_store.append_fact(session_id, f"Follow-up: {question[:180]}", tema=memory.tema or "seguimiento_caso")
        tools_used.append("guardar_memoria_caso")
        return AgentTurn(
            text=text,
            tools_used=tools_used,
            plan_lines=plan.as_lines(),
            task_kind=plan.kind.value,
        )

    return None


def _orchestrated_sensitive(
    plan: ExecutionPlan,
    question: str,
    session_id: str,
    profile: dict[str, str] | None,
) -> AgentTurn:
    """
    Caso sensible en modo local: no inventar respuesta desde un chunk RAG irrelevante.
    Mantiene búsqueda para fuentes en UI + ticket INT.
    """
    tools_used: list[str] = ["buscar_politicas_internas"]
    docs = list(get_retriever(SourceType.INTERNAL).invoke(question))
    if any(k in question.lower() for k in ("ley", "código", "codigo", "karin", "acoso", "finiquito")):
        tools_used.append("buscar_normativa_externa")
        docs.extend(get_retriever(SourceType.EXTERNAL).invoke(question))

    tools_used.extend(["guardar_memoria_caso", "registrar_ticket_gestion_personas"])
    _memory_store.append_fact(session_id, f"Caso sensible: {question[:200]}", tema=plan.kind.value)

    ticket = _ticket_client.create(
        asunto=f"Caso sensible — {question[:80]}",
        descripcion=f"Escalamiento automático desde agente. Detalle: {question}",
        categoria="ley_karin" if "acoso" in question.lower() else "otro",
        prioridad="alta",
        colaborador=(profile or {}).get("nombre", ""),
        rut=(profile or {}).get("rut", ""),
    )
    _memory_store.register_ticket(session_id, ticket.id)
    nombre = (profile or {}).get("nombre") or "Gestión de Personas"
    text = (
        f"{SENSITIVE_ESCALATION_REPLY}\n\n"
        f"He registrado el ticket **{ticket.id}** para seguimiento de **{nombre}**."
    )
    return AgentTurn(
        text=text,
        sources=_collect_sources(docs),
        tickets=[ticket.to_public_dict()],
        tools_used=tools_used,
        plan_lines=plan.as_lines(),
        task_kind=plan.kind.value,
    )


def initialize_agent():
    get_rag_chain()
    return True


def _execute_orchestrated_plan(
    plan: ExecutionPlan,
    question: str,
    chat_history: str,
    session_id: str,
    profile: dict[str, str] | None,
) -> AgentTurn:
    """Modo local / fallback: ejecuta el plan sin tool-calling LLM."""
    from src.guardrails import apply_response_guardrails

    tools_used: list[str] = []
    tickets: list[dict] = []
    pipeline = get_rag_chain()

    if plan.kind is TaskKind.OUT_OF_DOMAIN:
        return AgentTurn(
            text=DERIVATION_PHRASE,
            plan_lines=plan.as_lines(),
            task_kind=plan.kind.value,
            tools_used=["validar_dominio"],
        )

    if plan.kind is TaskKind.FOLLOW_UP:
        follow_turn = _orchestrated_follow_up(plan, question, session_id)
        if follow_turn is not None:
            return follow_turn

    if plan.kind is TaskKind.SENSITIVE and uses_local_generator():
        return _orchestrated_sensitive(plan, question, session_id, profile)

    docs = []
    if plan.kind in {TaskKind.FAQ, TaskKind.MULTI_STEP, TaskKind.SENSITIVE}:
        tools_used.append("buscar_politicas_internas")
        docs.extend(get_retriever(SourceType.INTERNAL).invoke(question))
        if plan.kind in {TaskKind.MULTI_STEP, TaskKind.SENSITIVE} or "ley" in question.lower():
            tools_used.append("buscar_normativa_externa")
            docs.extend(get_retriever(SourceType.EXTERNAL).invoke(question))
        elif "karin" in question.lower() or "acoso" in question.lower():
            tools_used.append("buscar_normativa_externa")
            docs.extend(get_retriever(SourceType.EXTERNAL).invoke(question))

    answer, used_docs = pipeline.answer_with_docs(question, docs, chat_history)
    answer = apply_response_guardrails(answer)
    tools_used.append("sintetizar_respuesta")

    if plan.kind in {TaskKind.MULTI_STEP, TaskKind.FOLLOW_UP, TaskKind.SENSITIVE}:
        tools_used.append("guardar_memoria_caso")
        _memory_store.append_fact(session_id, f"Consulta: {question[:200]}", tema=plan.kind.value)

    if plan.kind is TaskKind.SENSITIVE:
        tools_used.append("registrar_ticket_gestion_personas")
        ticket = _ticket_client.create(
            asunto=f"Caso sensible — {question[:80]}",
            descripcion=f"Escalamiento automático desde agente. Detalle: {question}",
            categoria="ley_karin" if "acoso" in question.lower() else "otro",
            prioridad="alta",
            colaborador=(profile or {}).get("nombre", ""),
            rut=(profile or {}).get("rut", ""),
        )
        _memory_store.register_ticket(session_id, ticket.id)
        tickets.append(ticket.to_public_dict())
        nombre = (profile or {}).get("nombre") or "Gestión de Personas"
        answer = (
            f"{answer}\n\n"
            f"He registrado el ticket **{ticket.id}** para seguimiento de {nombre}."
        )

    return AgentTurn(
        text=answer,
        sources=_collect_sources(used_docs),
        tickets=tickets,
        tools_used=tools_used,
        plan_lines=plan.as_lines(),
        task_kind=plan.kind.value,
    )


def run_tool_agent(
    question: str,
    history: list[dict[str, str]],
    session_id: str,
    profile: dict[str, str] | None,
    plan: ExecutionPlan,
    case_block: str,
) -> AgentTurn:
    set_agent_context(session_id, profile)
    tools_used: list[str] = []
    tickets_created: list[dict] = []

    system = AGENT_SYSTEM_PROMPT.format(
        plan="\n".join(plan.as_lines()),
        case_memory=case_block,
        profile=_profile_text(profile),
    )
    messages: list[Any] = [
        SystemMessage(content=system),
        *_history_to_lc(history),
        HumanMessage(content=question),
    ]
    llm = create_llm().bind_tools(AGENT_TOOLS)

    for _ in range(AGENT_MAX_TOOL_TURNS):
        ai: AIMessage = llm.invoke(messages)
        messages.append(ai)
        calls = getattr(ai, "tool_calls", None) or []
        if not calls:
            docs = consume_retrieved_docs()
            if not docs:
                docs = get_retriever().invoke(question)
            return AgentTurn(
                text=_content_to_text(ai.content) or DERIVATION_PHRASE,
                sources=_collect_sources(docs),
                tickets=tickets_created,
                tools_used=tools_used,
                plan_lines=plan.as_lines(),
                task_kind=plan.kind.value,
            )
        for call in calls:
            name = call.get("name") or ""
            args = call.get("args") or {}
            tool_id = call.get("id") or name
            tools_used.append(name)
            chosen = TOOL_MAP.get(name)
            if chosen is None:
                result = f"Herramienta desconocida: {name}"
            else:
                result = chosen.invoke(args)
                if name == "registrar_ticket_gestion_personas":
                    try:
                        payload = json.loads(str(result))
                        if payload.get("ok") and payload.get("ticket"):
                            tickets_created.append(payload["ticket"])
                    except json.JSONDecodeError:
                        pass
            messages.append(ToolMessage(content=str(result), tool_call_id=tool_id))

    docs = consume_retrieved_docs() or get_retriever().invoke(question)
    return AgentTurn(
        text=(
            "Necesito un poco más de contexto para cerrar tu solicitud. "
            "¿Confirmas que abra un ticket en Gestión de Personas?"
        ),
        sources=_collect_sources(docs),
        tickets=tickets_created,
        tools_used=tools_used,
        plan_lines=plan.as_lines(),
        task_kind=plan.kind.value,
    )


def run_agent(
    question: str,
    history: list[dict[str, str]],
    session_id: str,
    profile: dict[str, str] | None = None,
) -> AgentTurn:
    memory = _memory_store.load(session_id)
    has_case = bool(memory.facts or memory.ticket_ids or memory.tema)
    follow = _is_follow_up(history)
    plan = plan_for_question(
        question,
        has_case_memory=has_case,
        is_follow_up=follow,
    )
    case_block = memory.to_prompt_block()
    chat_history = format_chat_history(history)

    if profile:
        _memory_store.update_profile(
            session_id,
            colaborador=profile.get("nombre", ""),
            rut=profile.get("rut", ""),
        )

    if uses_local_generator():
        return _execute_orchestrated_plan(
            plan, question, chat_history, session_id, profile
        )

    set_agent_context(session_id, profile)
    try:
        return run_tool_agent(question, history, session_id, profile, plan, case_block)
    except Exception as exc:
        if _is_rate_limit(exc):
            return _fallback_to_local_orchestration(
                plan, question, chat_history, session_id, profile
            )
        raise


__all__ = ["AgentTurn", "initialize_agent", "run_agent"]
