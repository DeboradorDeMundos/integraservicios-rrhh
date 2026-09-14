# src/config.py
"""
IE1 — Diagnóstico organizacional y parámetros técnicos centralizados.

IntegraServicios S.A. recibe ~750 tickets/mes en Gestión de Personas.
IntegraBot apunta a autogestión 24/7 con respuesta < 5 s y 0 % invención
de datos normativos (derivación explícita si no hay evidencia documental).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SourceType(str, Enum):
    """Clasificación del corpus RAG (IE3: fuentes internas y externas)."""

    INTERNAL = "interno"
    EXTERNAL = "externo"


@dataclass(frozen=True)
class OrgCase:
    """Caso organizacional modelado en código (IE1)."""

    company: str = "IntegraServicios S.A."
    product: str = "IntegraBot"
    area: str = "Gestión de Personas"
    monthly_tickets: int = 750
    target_latency_seconds: int = 5
    escalation_team: str = "Gestión de Personas"


ORG_CASE = OrgCase()

# Corpus dual: documentos internos de la empresa + normativa externa chilena.
CORPUS: dict[str, SourceType] = {
    "RIOHS_IntegraServicios_2026.pdf": SourceType.INTERNAL,
    "Contrato_Colectivo_2026.pdf": SourceType.INTERNAL,
    "Codigo_del_Trabajo_Chile.pdf": SourceType.EXTERNAL,
}

CORPUS_LABELS: dict[SourceType, str] = {
    SourceType.INTERNAL: "Documento interno IntegraServicios",
    SourceType.EXTERNAL: "Normativa externa (Código del Trabajo / Ley Karin)",
}

PERSIST_DIRECTORY = "./chroma_db_v2"
DATA_DIRECTORY = "./data"
INDEX_VERSION = "v2-source-type"

EMBEDDING_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-2.5-flash"
LLM_TEMPERATURE = 0.1

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNK_SEPARATORS = [
    "\n\n",
    "\n",
    "Artículo",
    "Articulo",
    "Cláusula",
    "Clausula",
    "Ley N",
    " ",
    "",
]

RETRIEVER_K = 4
RETRIEVER_LAMBDA = 0.75
MAX_HISTORY_TURNS = 3

# Casos de demostración alineados con la rúbrica (IE3).
DEMO_QUESTIONS: tuple[str, ...] = (
    "¿Cuál es el valor del bono de colación?",
    "¿Cuántos días administrativos pagados tengo?",
    "¿Cuánto es el bono de escolaridad?",
    "¿Cómo se denuncia el acoso laboral (Ley Karin)?",
    "¿Cómo se calculan las horas extraordinarias?",
    "¿Mañana va a llover?",
)


def source_type_for_filename(filename: str) -> SourceType:
    """Resuelve el tipo de corpus a partir del nombre del PDF."""
    return CORPUS.get(filename, SourceType.INTERNAL)
