# src/conversation.py
"""
IE4 — Control de contexto conversacional acotado.

IntegraBot no mantiene memoria infinita: se inyectan las últimas
N interacciones al prompt para resolver follow-ups sin desbordar tokens.
"""
from __future__ import annotations

from src.config import MAX_HISTORY_TURNS


def format_chat_history(messages: list[dict], max_turns: int = MAX_HISTORY_TURNS) -> str:
    """
    Formatea el historial reciente para el System Prompt.

    Omite mensajes pendientes, errores y el turno en curso.
    """
    lines: list[str] = []
    for message in messages:
        if message.get("pending") or message.get("error"):
            continue
        role = message.get("role")
        content = (message.get("content") or "").strip()
        if not content:
            continue
        if role == "user":
            lines.append(f"Trabajador: {content[:600]}")
        elif role == "assistant":
            lines.append(f"IntegraBot: {content[:600]}")

    if not lines:
        return "Sin conversación previa."

    max_lines = max_turns * 2
    recent = lines[-max_lines:]
    return "\n".join(recent)
