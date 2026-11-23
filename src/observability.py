"""
EP3 — Observabilidad de IntegraBot.

Cada turno del agente deja un evento en JSONL: latencia, CPU, memoria,
herramientas, citas y resultado. El registro no guarda RUT, correo ni
nombre. Las métricas (precisión, consistencia, errores, latencia y
recursos) se calculan después, sobre esos eventos.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import statistics
import time
import tracemalloc
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Iterator

from src.config import ORG_CASE

OBS_DIR = os.getenv("OBSERVABILITY_DIR", "./observability")
CHAT_LOG = "runs.jsonl"
EVAL_LOG = "ep3_eval.jsonl"
SUMMARY_NAME = "ep3_summary.json"
SLO_MS = float(os.getenv("OBSERVABILITY_SLO_MS", str(ORG_CASE.target_latency_seconds * 1000)))
_process_phase = {"cold": True}

_RUT = re.compile(r"\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b")
_EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
_TOKEN = re.compile(r"[a-z0-9áéíóúñ$]+", re.IGNORECASE)

_meta: ContextVar[dict[str, Any]] = ContextVar("integrabot_obs_meta", default={})


def _phase() -> str:
    """El primer turno del proceso incluye la carga del índice."""
    if _process_phase["cold"]:
        _process_phase["cold"] = False
        return "cold_start"
    return "warm"


def observability_enabled() -> bool:
    return os.getenv("OBSERVABILITY_ENABLED", "1").strip().lower() not in {"0", "false", "no"}


def redact(text: str, limit: int = 320) -> str:
    """Quita identificadores personales antes de persistir un texto."""
    cleaned = _EMAIL.sub("[EMAIL]", _RUT.sub("[RUT]", text or ""))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rsplit(" ", 1)[0] + "…"


def session_ref(session_id: str) -> str:
    raw = (session_id or "anon").encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:12]


@contextmanager
def evaluation_meta(**fields: Any) -> Iterator[None]:
    """Metadatos de la batería EP3 (intent, expect). No se usan en el chat."""
    token = _meta.set(fields)
    try:
        yield
    finally:
        _meta.reset(token)


def _path(name: str) -> str:
    os.makedirs(OBS_DIR, exist_ok=True)
    return os.path.join(OBS_DIR, name)


def append_event(record: dict[str, Any], filename: str) -> None:
    path = _path(filename)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def reset_log(filename: str) -> None:
    path = _path(filename)
    with open(path, "w", encoding="utf-8"):
        pass


def load_events(*filenames: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in filenames:
        path = os.path.join(OBS_DIR, name)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    rows.sort(key=lambda item: item.get("ts") or "")
    return rows


class _TurnRecorder:
    def __init__(self, question: str, session_id: str, log_name: str) -> None:
        self.question = question
        self.session_id = session_id
        self.log_name = log_name
        self.started = time.perf_counter()
        self.cpu_started = time.process_time()
        self._tracing = False
        self.error: str | None = None
        self.turn: Any = None

    def __enter__(self) -> "_TurnRecorder":
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            self._tracing = True
        return self

    def attach(self, turn: Any) -> None:
        self.turn = turn

    def fail(self, exc: BaseException) -> None:
        self.error = type(exc).__name__

    def __exit__(self, exc_type, exc, _tb) -> bool:
        if exc is not None and self.error is None:
            self.error = type(exc).__name__
        try:
            self._flush()
        except Exception:
            pass
        if self._tracing:
            tracemalloc.stop()
        return False

    def _flush(self) -> None:
        if not observability_enabled():
            return
        latency_ms = (time.perf_counter() - self.started) * 1000
        cpu_ms = (time.process_time() - self.cpu_started) * 1000
        peak_kb = 0.0
        if tracemalloc.is_tracing():
            _current, peak = tracemalloc.get_traced_memory()
            peak_kb = round(peak / 1024, 1)

        meta = dict(_meta.get() or {})
        turn = self.turn
        text = getattr(turn, "text", "") or ""
        tools = list(getattr(turn, "tools_used", []) or [])
        tickets = list(getattr(turn, "tickets", []) or [])
        sources = list(getattr(turn, "sources", []) or [])
        task_kind = getattr(turn, "task_kind", "") or ""
        plan_lines = list(getattr(turn, "plan_lines", []) or [])

        from src.guardrails import extract_citations, has_derivation_phrase

        citations = extract_citations(text)
        derived = has_derivation_phrase(text)
        ticket_ids = [str(item.get("id")) for item in tickets if isinstance(item, dict) and item.get("id")]
        source_files = sorted({str(item.get("name")) for item in sources if isinstance(item, dict) and item.get("name")})

        events = [{"step": "inicio", "detail": meta.get("suite") or "chat"}]
        if task_kind:
            events.append({"step": "plan", "detail": task_kind})
        for tool in tools:
            events.append({"step": "tool", "detail": tool})
        if self.error:
            events.append({"step": "error", "detail": self.error})
        elif derived:
            events.append({"step": "guardrail", "detail": "derivacion"})
        elif citations:
            events.append({"step": "guardrail", "detail": "citado"})
        events.append({"step": "fin", "detail": f"{latency_ms:.0f} ms"})

        record = {
            "run_id": uuid.uuid4().hex[:12],
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "suite": meta.get("suite") or "chat",
            "session": session_ref(self.session_id),
            "intent": meta.get("intent") or "",
            "expect": meta.get("expect") or "",
            "repeat": int(meta.get("repeat") or 1),
            "question": redact(self.question),
            "task_kind": task_kind,
            "tools": tools,
            "plan": plan_lines[:6],
            "latency_ms": round(latency_ms, 1),
            "cpu_ms": round(cpu_ms, 1),
            "peak_kb": peak_kb,
            "citations": citations,
            "derived": derived,
            "ticket_ids": ticket_ids,
            "source_files": source_files,
            "error": self.error,
            "answer_excerpt": redact(text, 280),
            "answer_chars": len(text),
            "slo_ms": SLO_MS,
            "slo_ok": latency_ms <= SLO_MS and not self.error,
            "events": events,
        }
        record["phase"] = _phase()
        record["precise"] = is_precise(record)
        append_event(record, self.log_name)


@contextmanager
def record_agent_turn(
    question: str,
    session_id: str,
    *,
    log_name: str | None = None,
) -> Iterator[_TurnRecorder]:
    name = log_name or os.getenv("OBSERVABILITY_LOG", CHAT_LOG)
    recorder = _TurnRecorder(question, session_id, name)
    with recorder:
        yield recorder


def is_precise(record: dict[str, Any]) -> bool | None:
    """
    Precisión contra la etiqueta del escenario.

    None si el turno no trae etiqueta (chat libre): no entra al porcentaje.
    """
    if record.get("error"):
        return False
    expect = (record.get("expect") or "").strip()
    if not expect:
        return None
    citations = record.get("citations") or []
    derived = bool(record.get("derived"))
    tickets = record.get("ticket_ids") or []
    if expect in {"cita", "cita_interna"}:
        return bool(citations) and not derived
    if expect == "derivacion":
        return derived and not citations
    if expect == "ticket":
        return bool(tickets)
    return False


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    rank = (len(ordered) - 1) * (pct / 100)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    weight = rank - low
    return float(ordered[low] + (ordered[high] - ordered[low]) * weight)


def _tokens(text: str) -> set[str]:
    normalized = (
        (text or "")
        .lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
    )
    return {token for token in _TOKEN.findall(normalized) if len(token) > 2 or token.startswith("$")}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def _amounts(text: str) -> set[str]:
    return set(re.findall(r"\$\s?[\d.]+", text or ""))


def compute_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Agrega precisión, latencia, consistencia, errores y recursos."""
    labeled = [row for row in records if row.get("expect")]
    precise_flags = [bool(row.get("precise")) for row in labeled]
    latencies = [float(row.get("latency_ms") or 0) for row in records]
    cpus = [float(row.get("cpu_ms") or 0) for row in records]
    peaks = [float(row.get("peak_kb") or 0) for row in records]
    errors = [row for row in records if row.get("error")]
    slo_fail = [row for row in records if not row.get("slo_ok")]

    by_intent: dict[str, list[dict[str, Any]]] = {}
    for row in records:
        key = row.get("intent") or row.get("question") or "sin_intent"
        by_intent.setdefault(key, []).append(row)

    consistency_rows = []
    pair_scores: list[float] = []
    amount_conflicts = 0
    for intent, group in sorted(by_intent.items()):
        if len(group) < 2:
            continue
        scores = []
        excerpts = [row.get("answer_excerpt") or "" for row in group]
        for i in range(len(excerpts)):
            for j in range(i + 1, len(excerpts)):
                scores.append(_jaccard(_tokens(excerpts[i]), _tokens(excerpts[j])))
        amounts = [_amounts(text) for text in excerpts]
        nonempty = [item for item in amounts if item]
        conflict = len({frozenset(item) for item in nonempty}) > 1
        if conflict:
            amount_conflicts += 1
        mean_score = statistics.fmean(scores) if scores else 1.0
        pair_scores.append(mean_score)
        consistency_rows.append(
            {
                "intent": intent,
                "n": len(group),
                "jaccard": round(mean_score, 3),
                "monto_estable": not conflict,
            }
        )

    by_expect: dict[str, dict[str, int]] = {}
    for row in labeled:
        bucket = by_expect.setdefault(row["expect"], {"n": 0, "ok": 0})
        bucket["n"] += 1
        if row.get("precise"):
            bucket["ok"] += 1

    kind_latency: dict[str, list[float]] = {}
    for row in records:
        kind_latency.setdefault(row.get("task_kind") or "sin_plan", []).append(float(row.get("latency_ms") or 0))

    precision = (sum(precise_flags) / len(precise_flags)) if precise_flags else None
    return {
        "n": len(records),
        "n_labeled": len(labeled),
        "precision": None if precision is None else round(precision, 4),
        "precision_by_expect": {
            key: {
                "n": val["n"],
                "ok": val["ok"],
                "rate": round(val["ok"] / val["n"], 4) if val["n"] else 0,
            }
            for key, val in sorted(by_expect.items())
        },
        "error_rate": round(len(errors) / len(records), 4) if records else 0,
        "error_count": len(errors),
        "slo_ms": SLO_MS,
        "slo_breach_count": len(slo_fail),
        "slo_compliance": round(1 - (len(slo_fail) / len(records)), 4) if records else 0,
        "latency_ms": {
            "mean": round(statistics.fmean(latencies), 1) if latencies else 0,
            "p50": round(_percentile(latencies, 50), 1),
            "p95": round(_percentile(latencies, 95), 1),
            "max": round(max(latencies), 1) if latencies else 0,
        },
        "cpu_ms": {
            "mean": round(statistics.fmean(cpus), 1) if cpus else 0,
            "p95": round(_percentile(cpus, 95), 1),
        },
        "peak_kb": {
            "mean": round(statistics.fmean(peaks), 1) if peaks else 0,
            "max": round(max(peaks), 1) if peaks else 0,
        },
        "consistency": round(statistics.fmean(pair_scores), 4) if pair_scores else None,
        "consistency_by_intent": consistency_rows,
        "amount_conflicts": amount_conflicts,
        "latency_by_kind": {
            kind: round(statistics.fmean(vals), 1) for kind, vals in sorted(kind_latency.items())
        },
    }


def analyze(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Hallazgos y recomendaciones a partir de las métricas observadas."""
    metrics = compute_metrics(records)
    findings: list[str] = []
    recommendations: list[dict[str, str]] = []

    lat = metrics["latency_ms"]
    if records:
        first = records[0].get("latency_ms") or 0
        rest = [float(row.get("latency_ms") or 0) for row in records[1:]]
        if rest and first > statistics.fmean(rest) * 2 and first > 1500:
            findings.append(
                f"El primer turno ({first:.0f} ms) es el cuello de botella: carga del índice y del modelo de embeddings. "
                f"La media del resto es {statistics.fmean(rest):.0f} ms."
            )
            recommendations.append(
                {
                    "titulo": "Separar el arranque en frío del SLO de respuesta",
                    "detalle": (
                        "Precargar Chroma y el modelo de embeddings al iniciar Streamlit, "
                        "y medir el SLO de 5 s solo en turnos tibios. El arranque no debe "
                        "contarse como una consulta de colaborador."
                    ),
                    "evidencia": "Latencia del primer evento frente a la media de los siguientes.",
                }
            )

    if metrics["slo_breach_count"]:
        findings.append(
            f"{metrics['slo_breach_count']} de {metrics['n']} turnos superan el SLO de {int(SLO_MS)} ms "
            f"o terminan en error (p95 = {lat['p95']} ms)."
        )
    elif records:
        findings.append(
            f"Latencia dentro del SLO de {int(SLO_MS) / 1000:.0f} s: "
            f"media {lat['mean']} ms, p50 {lat['p50']} ms, p95 {lat['p95']} ms."
        )

    precision = metrics["precision"]
    if precision is not None and precision < 0.9:
        weak = [
            f"{name} {bucket['ok']}/{bucket['n']}"
            for name, bucket in metrics["precision_by_expect"].items()
            if bucket["rate"] < 1
        ]
        findings.append(
            "La precisión cae al variar la redacción. "
            + ("; ".join(weak) if weak else f"Global {precision:.0%}.")
        )
        recommendations.append(
            {
                "titulo": "Evaluar paráfrasis, no solo la pregunta de la demo",
                "detalle": (
                    "Incorporar la batería de variabilidad al smoke test. "
                    "Si un sinónimo no recupera el mismo monto, el retriever o el "
                    "generador local deben ajustarse antes de subir temperatura del LLM."
                ),
                "evidencia": "precision_by_expect en ep3_summary.json.",
            }
        )
    elif precision is not None:
        findings.append(f"Precisión en escenarios etiquetados: {precision:.0%} ({metrics['n_labeled']} turnos).")

    consistency = metrics["consistency"]
    if consistency is not None and consistency < 0.75:
        findings.append(
            f"Consistencia Jaccard media {consistency:.0%}. "
            f"Conflictos de monto entre repeticiones: {metrics['amount_conflicts']}."
        )
        recommendations.append(
            {
                "titulo": "Fijar la respuesta de beneficios en el fragmento citado",
                "detalle": (
                    "Con temperature 0.1 el modelo aún puede parafrasear cifras. "
                    "Extraer el monto del chunk ganador y no dejar que el LLM lo reescriba."
                ),
                "evidencia": "consistency_by_intent y amount_conflicts.",
            }
        )
    elif consistency is not None:
        findings.append(f"Consistencia entre repeticiones y paráfrasis: Jaccard {consistency:.0%}.")

    if metrics["error_count"]:
        findings.append(f"Frecuencia de errores: {metrics['error_rate']:.0%} ({metrics['error_count']} fallos).")
        recommendations.append(
            {
                "titulo": "Alertar cuando la tasa de error supere 2 %",
                "detalle": "El dashboard ya marca turnos con excepción. En producción, ese umbral abre un aviso a Gestión de Personas.",
                "evidencia": "Campo error en el JSONL.",
            }
        )
    elif records:
        findings.append("Frecuencia de errores en la batería: 0 %.")

    if metrics["peak_kb"]["max"]:
        findings.append(
            f"Memoria Python del turno (pico tracemalloc): media {metrics['peak_kb']['mean']} KB, "
            f"máximo {metrics['peak_kb']['max']} KB. CPU media {metrics['cpu_ms']['mean']} ms."
        )

    misses = [row for row in records if row.get("expect") and row.get("precise") is False]
    if misses:
        sample = misses[0]
        findings.append(
            f"Fallo representativo: intent «{sample.get('intent')}» esperaba {sample.get('expect')} "
            f"y obtuvo «{(sample.get('answer_excerpt') or '')[:140]}»."
        )

    recommendations.append(
        {
            "titulo": "Conservar el registro local y sin datos personales",
            "detalle": (
                "El JSONL vive en el servidor de la app, con RUT y correo redactados "
                "y la sesión hasheada. No se reenvía el texto completo a un tercero "
                "de observabilidad."
            ),
            "evidencia": "redact() y session_ref() en src/observability.py.",
        }
    )
    recommendations.append(
        {
            "titulo": "Escalar por tipo de tarea, no por un solo promedio",
            "detalle": (
                "Un promedio esconde que un caso sensible abre ticket y consulta dos corpus. "
                "El dashboard separa latencia por task_kind para decidir caché, no para recortar guardrails."
            ),
            "evidencia": "latency_by_kind.",
        }
    )

    return {"metrics": metrics, "findings": findings, "recommendations": recommendations}


def write_summary(payload: dict[str, Any], filename: str = SUMMARY_NAME) -> str:
    path = _path(filename)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return path
