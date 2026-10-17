# src/config.py
"""
IE1 — Diagnóstico organizacional y parámetros técnicos centralizados.

IntegraServicios S.A. recibe ~750 tickets/mes en Gestión de Personas.
IntegraBot apunta a autogestión 24/7 con respuesta < 5 s y 0 % invención
de datos normativos (derivación explícita si no hay evidencia documental).
"""
from __future__ import annotations

import os
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

DATA_DIRECTORY = "./data"

# google | groq | local  — local no requiere API (ideal si se agotó la cuota de Google)
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "google").strip().lower()

EMBEDDING_MODEL = "gemini-embedding-001"
HF_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# Override en .env si hay 429: GOOGLE_LLM_MODEL=gemini-2.5-flash
LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL", "gemini-3.6-flash").strip()
GROQ_LLM_MODEL = os.getenv("GROQ_LLM_MODEL", "llama-3.1-8b-instant")
LLM_TEMPERATURE = 0.1

_INDEX_BY_PROVIDER = {
    "google": ("./chroma_db_v2", "v2-source-type-gemini"),
    "groq": ("./chroma_db_groq", "v2-source-type-hf"),
    "local": ("./chroma_db_local", "v2-source-type-hf"),
}
PERSIST_DIRECTORY, INDEX_VERSION = _INDEX_BY_PROVIDER.get(
    MODEL_PROVIDER, _INDEX_BY_PROVIDER["google"]
)

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

# EP2 — Agente: memoria de caso, planificación y tickets RRHH
CASE_MEMORY_DIR = "./case_memory"
AGENT_MAX_TOOL_TURNS = 4
AGENT_HISTORY_LIMIT = 8

SENSITIVE_HR_KEYWORDS: tuple[str, ...] = (
    "finiquito",
    "sumario",
    "litig",
    "litigioso",
    "cheque",
    "judicial",
    "despido injustificado",
    "denuncia penal",
    "acoso sexual",
)

OUT_OF_DOMAIN_HINTS: tuple[str, ...] = (
    "llover",
    "clima",
    "fútbol",
    "futbol",
    "partido",
    "bitcoin",
    "receta de",
)

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
