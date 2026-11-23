#!/usr/bin/env python
"""
Batería EP3 — observabilidad con variabilidad de redacción.

Mide precisión, latencia, consistencia, errores y recursos sobre el agente
ya construido. Por defecto usa MODEL_PROVIDER=local (sin cuota de API).

Uso:
    python scripts/observability_eval.py
    python scripts/observability_eval.py --live
"""
from __future__ import annotations

import argparse
import os
import sys
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from dotenv import load_dotenv

load_dotenv()

from src.observability import (  # noqa: E402
    EVAL_LOG,
    analyze,
    evaluation_meta,
    is_precise,
    load_events,
    redact,
    reset_log,
    write_summary,
)

# Misma intención, distinta redacción: variabilidad de datos de entrada.
SCENARIOS: list[tuple[str, str, str]] = [
    ("colacion", "cita_interna", "¿Cuál es el valor del bono de colación?"),
    ("colacion", "cita_interna", "¿Cuánto es el bono de colación para jornada completa?"),
    ("dias_admin", "cita_interna", "¿Cuántos días administrativos pagados tengo?"),
    ("dias_admin", "cita_interna", "¿A cuántos días administrativos pagados tengo derecho?"),
    ("escolaridad", "cita_interna", "¿Cuánto es el bono de escolaridad?"),
    ("escolaridad", "cita_interna", "¿Cuál es el monto del bono de escolaridad?"),
    ("aguinaldo", "cita_interna", "¿Cuánto es el aguinaldo de Fiestas Patrias?"),
    ("karin", "cita", "¿Cómo se denuncia el acoso laboral (Ley Karin)?"),
    ("karin", "cita", "¿Cuál es el canal para denunciar acoso laboral según Ley Karin?"),
    ("horas_extra", "cita", "¿Cómo se calculan las horas extraordinarias?"),
    ("horas_extra", "cita", "¿Cuál es el recargo de las horas extraordinarias?"),
    ("clima", "derivacion", "¿Mañana va a llover?"),
    ("clima", "derivacion", "¿Cuál es el pronóstico del clima para mañana?"),
    ("fuera_dominio", "derivacion", "¿Quién gana el partido de fútbol hoy?"),
    ("sensible", "ticket", "Necesito orientación por un finiquito litigioso"),
    ("sensible", "ticket", "Hay un cheque litigioso asociado a mi despido"),
    (
        "privacidad",
        "cita_interna",
        "¿Cuál es el valor del bono de colación? Mi RUT es 19.914.672-6",
    ),
]


def _check_metric_rules() -> None:
    sample_ok = {
        "expect": "cita",
        "citations": ["Contrato_Colectivo_2026.pdf"],
        "derived": False,
        "ticket_ids": [],
        "error": None,
    }
    sample_bad = {
        "expect": "derivacion",
        "citations": ["Contrato_Colectivo_2026.pdf"],
        "derived": False,
        "ticket_ids": [],
        "error": None,
    }
    if is_precise(sample_ok) is not True or is_precise(sample_bad) is not False:
        raise SystemExit("FAIL regla de precisión")
    hidden = redact("consulta RUT 19.914.672-6 y correo ana@duoc.cl")
    if "19.914.672-6" in hidden or "ana@duoc.cl" in hidden:
        raise SystemExit("FAIL redacción de datos personales")
    if "[RUT]" not in hidden or "[EMAIL]" not in hidden:
        raise SystemExit("FAIL marcadores de redacción")
    print("  OK  reglas de precisión y privacidad")


def run_suite(repeats: int) -> list[dict]:
    from src.agent import run_agent

    os.environ["OBSERVABILITY_LOG"] = EVAL_LOG
    reset_log(EVAL_LOG)
    session_id = f"ep3-{uuid.uuid4().hex[:8]}"
    total = len(SCENARIOS) * repeats
    done = 0
    for repeat in range(1, repeats + 1):
        for intent, expect, question in SCENARIOS:
            done += 1
            print(f"  [{done}/{total}] {intent} · {question[:64]}")
            with evaluation_meta(suite="ep3_eval", intent=intent, expect=expect, repeat=repeat):
                run_agent(question, [], session_id, profile=None)
    rows = load_events(EVAL_LOG)
    raw = open(os.path.join("observability", EVAL_LOG), encoding="utf-8").read()
    if "19.914.672-6" in raw or "19914672" in raw:
        raise SystemExit("FAIL el log de observabilidad conservó un RUT")
    print("  OK  el JSONL no conserva el RUT de prueba")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Usa el MODEL_PROVIDER del .env")
    parser.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args()

    print("\n[EP3] Reglas de métrica")
    _check_metric_rules()

    if not args.live:
        os.environ["MODEL_PROVIDER"] = "local"
        print("\n[EP3] Proveedor: local (sin API)")
    else:
        print("\n[EP3] Proveedor del entorno (.env)")

    print("\n[EP3] Batería con variabilidad")
    rows = run_suite(max(1, args.repeats))
    report = analyze(rows)
    path = write_summary(report)
    metrics = report["metrics"]
    precision = metrics["precision"]
    precision_txt = "n/a" if precision is None else f"{precision:.0%}"
    consistency = metrics["consistency"]
    consistency_txt = "n/a" if consistency is None else f"{consistency:.0%}"
    print("\n[EP3] Resumen")
    print(f"  turnos            {metrics['n']}")
    print(f"  precisión         {precision_txt}")
    print(f"  consistencia      {consistency_txt}")
    print(f"  errores           {metrics['error_rate']:.0%} ({metrics['error_count']})")
    print(
        "  latencia ms       "
        f"media {metrics['latency_ms']['mean']} · "
        f"p50 {metrics['latency_ms']['p50']} · "
        f"p95 {metrics['latency_ms']['p95']}"
    )
    print(
        f"  SLO {int(metrics['slo_ms'])} ms   "
        f"cumplimiento {metrics['slo_compliance']:.0%} · "
        f"fuera de SLO {metrics['slo_breach_count']}"
    )
    print(
        f"  recursos          CPU media {metrics['cpu_ms']['mean']} ms · "
        f"pico mem {metrics['peak_kb']['max']} KB"
    )
    print("\n[EP3] Hallazgos")
    for line in report["findings"]:
        print(f"  - {line}")
    misses = [row for row in rows if row.get("precise") is False]
    if misses:
        print("\n[EP3] Turnos imprecisos")
        for row in misses:
            print(
                f"  - {row.get('intent')} esperaba {row.get('expect')}: "
                f"{(row.get('answer_excerpt') or '')[:160]}"
            )
    print(f"\nResumen escrito en {path}")
    if misses:
        raise SystemExit(len(misses))


if __name__ == "__main__":
    main()
