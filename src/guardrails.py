# src/guardrails.py
"""
IE2 — Guardrails post-generación en código (complemento al System Prompt).

Verifica citas explícitas y normaliza la frase institucional de derivación.
"""
from __future__ import annotations

import re

from src.prompts import DERIVATION_PHRASE

CITATION_PATTERN = re.compile(
    r"\[Fuente:\s*([^,\]]+\.pdf)[^\]]*\]",
    flags=re.IGNORECASE,
)


def extract_citations(answer: str) -> list[str]:
    """PDFs citados en la respuesta del modelo."""
    return [match.group(1).strip() for match in CITATION_PATTERN.finditer(answer or "")]


def has_derivation_phrase(answer: str) -> bool:
    """True si la respuesta incluye la escalada institucional."""
    return DERIVATION_PHRASE in (answer or "")


def has_documented_evidence(answer: str) -> bool:
    """True si la respuesta cita al menos un PDF."""
    return bool(extract_citations(answer))


def apply_response_guardrails(answer: str) -> str:
    """
    Normaliza respuestas vacías o sin evidencia ni derivación explícita.

    Si el modelo devuelve texto vacío, fuerza la frase de derivación.
    """
    text = (answer or "").strip()
    if not text:
        return DERIVATION_PHRASE
    if not has_documented_evidence(text) and not has_derivation_phrase(text):
        return DERIVATION_PHRASE
    return text
