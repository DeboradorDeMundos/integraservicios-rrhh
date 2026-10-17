# src/planner.py
"""
IE5 — Planificación y priorización de tareas del agente.

Clasifica la consulta y genera un plan explícito (secuencia de pasos) que
el orquestador o el LLM con herramientas debe seguir.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from src.config import OUT_OF_DOMAIN_HINTS, SENSITIVE_HR_KEYWORDS


class TaskKind(str, Enum):
    FAQ = "consulta_documentada"
    MULTI_STEP = "consulta_multietapa"
    SENSITIVE = "caso_sensible"
    OUT_OF_DOMAIN = "fuera_de_dominio"
    FOLLOW_UP = "seguimiento_caso"


@dataclass
class PlanStep:
    order: int
    action: str
    rationale: str
    priority: str = "alta"


@dataclass
class ExecutionPlan:
    kind: TaskKind
    steps: list[PlanStep] = field(default_factory=list)
    summary: str = ""

    def as_lines(self) -> list[str]:
        return [f"{step.order}. [{step.priority}] {step.action} — {step.rationale}" for step in self.steps]


def _normalize(text: str) -> str:
    return (text or "").lower().strip()


def classify_task(question: str, *, has_case_memory: bool, is_follow_up: bool) -> TaskKind:
    q = _normalize(question)
    if any(hint in q for hint in OUT_OF_DOMAIN_HINTS):
        return TaskKind.OUT_OF_DOMAIN
    if any(word in q for word in SENSITIVE_HR_KEYWORDS):
        return TaskKind.SENSITIVE
    if is_follow_up and has_case_memory:
        return TaskKind.FOLLOW_UP
    if any(sep in q for sep in (" y ", " además ", " también ", " primero ", " luego ")):
        return TaskKind.MULTI_STEP
    if q.count("?") > 1:
        return TaskKind.MULTI_STEP
    return TaskKind.FAQ


def build_execution_plan(kind: TaskKind, question: str) -> ExecutionPlan:
    q_preview = question.strip()[:80]
    if kind is TaskKind.OUT_OF_DOMAIN:
        return ExecutionPlan(
            kind=kind,
            summary="Pregunta fuera del dominio RRHH; no se consulta corpus.",
            steps=[
                PlanStep(1, "Validar dominio", "Evitar alucinación en temas no laborales", "alta"),
                PlanStep(2, "Derivar a Gestión de Personas", "Frase institucional sin inventar datos", "alta"),
            ],
        )
    if kind is TaskKind.SENSITIVE:
        return ExecutionPlan(
            kind=kind,
            summary=f"Caso sensible detectado: {q_preview}",
            steps=[
                PlanStep(1, "Registrar contexto en memoria de caso", "Continuidad para RRHH humano", "alta"),
                PlanStep(2, "Buscar normativa/guía aplicable", "Solo orientación documentada", "media"),
                PlanStep(3, "Abrir ticket RRHH", "Escalamiento con trazabilidad", "alta"),
                PlanStep(4, "Responder con límites del copiloto", "No reemplazar sumario ni asesoría legal", "alta"),
            ],
        )
    if kind is TaskKind.MULTI_STEP:
        return ExecutionPlan(
            kind=kind,
            summary=f"Consulta multietapa: {q_preview}",
            steps=[
                PlanStep(1, "Buscar políticas internas", "Contrato y RIOHS primero", "alta"),
                PlanStep(2, "Buscar normativa externa si aplica", "Código del Trabajo / Ley Karin", "media"),
                PlanStep(3, "Sintetizar por subpregunta", "Separar RESPUESTO / DERIVADO", "alta"),
                PlanStep(4, "Guardar resumen en memoria de caso", "Follow-ups futuros", "media"),
            ],
        )
    if kind is TaskKind.FOLLOW_UP:
        return ExecutionPlan(
            kind=kind,
            summary=f"Seguimiento con memoria de caso: {q_preview}",
            steps=[
                PlanStep(1, "Recuperar memoria de caso", "Continuidad IE3", "alta"),
                PlanStep(2, "Consultar ticket o hechos previos", "Sin repetir RAG irrelevante", "alta"),
                PlanStep(3, "Responder en contexto del ticket/tema previo", "Coherencia conversacional", "alta"),
            ],
        )
    return ExecutionPlan(
        kind=kind,
        summary=f"FAQ documentada: {q_preview}",
        steps=[
            PlanStep(1, "Buscar políticas internas", "Beneficios y reglamento corporativo", "alta"),
            PlanStep(2, "Buscar normativa externa complementaria", "Solo si la pregunta lo requiere", "media"),
            PlanStep(3, "Generar respuesta con citas", "Guardrails anti-alucinación", "alta"),
        ],
    )


def plan_for_question(
    question: str,
    *,
    has_case_memory: bool,
    is_follow_up: bool,
) -> ExecutionPlan:
    kind = classify_task(question, has_case_memory=has_case_memory, is_follow_up=is_follow_up)
    return build_execution_plan(kind, question)
