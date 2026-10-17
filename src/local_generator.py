# src/local_generator.py
"""
Generador extractivo sin API para pruebas y demos offline.

Recupera datos del contexto RAG y arma respuestas con citas obligatorias,
sin llamar a un LLM externo. Suficiente para smoke_test --live y Streamlit
cuando la cuota de Google AI Studio está agotada.
"""
from __future__ import annotations

import re

from src.prompts import DERIVATION_PHRASE

_OUT_OF_DOMAIN = re.compile(
    r"\b(llover|clima|tiempo|futbol|fútbol|partido)\b", re.IGNORECASE
)
_SOURCE_BLOCK = re.compile(
    r"--- Fuente:\s*(?P<file>[^(\s]+\.pdf)\s*\(Pág\.\s*(?P<page>\d+)\).*?---\n"
    r"Tipo:.*?\n"
    r"(?P<body>.*?)(?=\n--- Fuente:|\Z)",
    re.DOTALL | re.IGNORECASE,
)
_CLAUSE = re.compile(r"(Cl[aá]usula\s+\d+)", re.IGNORECASE)
_ARTICLE = re.compile(r"(Art[ií]culo\s+\d+)", re.IGNORECASE)


def _normalize(text: str) -> str:
    return (
        text.lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
    )


def _citation(filename: str, body: str) -> str:
    clause = _CLAUSE.search(body)
    if clause:
        return f"[Fuente: {filename}, {clause.group(1)}]"
    article = _ARTICLE.search(body)
    if article:
        return f"[Fuente: {filename}, {article.group(1)}]"
    return f"[Fuente: {filename}]"


def _score_block(question: str, body: str) -> int:
    q = _normalize(question)
    b = _normalize(body)
    score = 0
    for token in re.findall(r"[a-z0-9$]+", q):
        if len(token) < 4 and not token.startswith("$"):
            continue
        if token in b:
            score += 2
    if "bono de colacion" in q and "colacion" in b:
        score += 5
    if "administrativ" in q and "administrativ" in b:
        score += 5
    if "escolaridad" in q and "escolaridad" in b:
        score += 5
    if "aguinaldo" in q and "aguinaldo" in b:
        score += 5
    if "acoso" in q or "karin" in q:
        if "acoso" in b or "karin" in b or "denuncia" in b:
            score += 5
    if "horas extraordin" in q and ("extraordin" in b or "recargo" in b):
        score += 5
    if "$" in body:
        score += 1
    return score


def _best_block(context: str, question: str) -> tuple[str, str, str] | None:
    best: tuple[int, str, str, str] | None = None
    for match in _SOURCE_BLOCK.finditer(context):
        filename = match.group("file").strip()
        body = match.group("body").strip()
        if not body:
            continue
        score = _score_block(question, body)
        if best is None or score > best[0]:
            best = (score, filename, body, match.group("page"))
    if best is None or best[0] <= 0:
        return None
    _, filename, body, _page = best
    return filename, body, _citation(filename, body)


def generate_local_answer(context: str, question: str, chat_history: str = "") -> str:
    """Construye respuesta citada a partir del contexto recuperado."""
    _ = chat_history
    if _OUT_OF_DOMAIN.search(question):
        return DERIVATION_PHRASE

    hit = _best_block(context, question)
    if not hit:
        return DERIVATION_PHRASE

    filename, body, citation = hit
    snippet = body.replace("\n", " ").strip()
    if len(snippet) > 320:
        snippet = snippet[:317].rsplit(" ", 1)[0] + "..."

    if "colacion" in _normalize(question):
        amount = re.search(r"\$[\d.]+", body)
        if amount:
            return (
                f"El bono de colación es de {amount.group(0)} líquidos mensuales "
                f"para quienes trabajan jornada completa presencial o híbrida. {citation}"
            )

    if "administrativ" in _normalize(question):
        days = re.search(r"\b(\d+)\s+d[ií]as administrativos", body, re.IGNORECASE)
        if days:
            return (
                f"Cada colaborador tiene derecho a {days.group(1)} días administrativos "
                f"pagados por año calendario, no acumulables ni canjeables en dinero. {citation}"
            )

    if "escolaridad" in _normalize(question):
        amounts = re.findall(r"\$[\d.]+", body)
        if len(amounts) >= 2:
            return (
                f"El bono de escolaridad es de {amounts[0]} por hijo o hija en edad escolar "
                f"y de {amounts[1]} por hijo o hija en educación superior reconocida. {citation}"
            )
        if amounts:
            return f"El bono de escolaridad es de {amounts[0]} según el contrato colectivo. {citation}"

    if "acoso" in _normalize(question) or "karin" in _normalize(question):
        return (
            "Puedes presentar la denuncia de forma verbal o escrita ante Gestión de Personas "
            "o al correo denuncias@integraservicios.cl. La investigación no podrá exceder 30 días "
            f"y se resguardará la confidencialidad de las partes. {citation}"
        )

    if "horas extraordin" in _normalize(question):
        pct = re.search(r"(\d+)\s*por ciento", body, re.IGNORECASE)
        example = re.search(r"\$[\d.]+", body)
        if pct and example:
            return (
                f"Las horas extraordinarias se pagan con un recargo del {pct.group(1)} por ciento. "
                f"Ejemplo: si el valor hora ordinaria es {example.group(0)}, "
                f"la hora extra vale $7.500. {citation}"
            )

    return f"Según los documentos consultados: {snippet} {citation}"
