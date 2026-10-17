#!/usr/bin/env python
"""
Escenarios EP2 — planificación, memoria, herramientas (offline-friendly).

Uso:
    python scripts/agent_scenarios_test.py
    python scripts/agent_scenarios_test.py --live
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

from src.agent import run_agent
from src.memory import CaseMemoryStore
from src.planner import TaskKind, plan_for_question
from src.guardrails import has_derivation_phrase


def ok(msg: str) -> None:
    print(f"  OK  {msg}")


def fail(msg: str, detail: str = "") -> None:
    print(f"  FAIL {msg}" + (f": {detail}" if detail else ""))
    raise SystemExit(1)


def test_planner() -> None:
    print("\n[IE5] Planificación")
    p1 = plan_for_question("¿Cuál es el bono de colación?", has_case_memory=False, is_follow_up=False)
    if p1.kind is not TaskKind.FAQ:
        fail("FAQ", p1.kind.value)
    ok(f"FAQ -> {len(p1.steps)} pasos")

    p2 = plan_for_question(
        "¿Cuántos días administrativos tengo y qué documentos debo presentar?",
        has_case_memory=False,
        is_follow_up=False,
    )
    if p2.kind is not TaskKind.MULTI_STEP:
        fail("multietapa", p2.kind.value)
    ok("consulta compuesta -> plan multietapa")

    p3 = plan_for_question("¿Mañana va a llover?", has_case_memory=False, is_follow_up=False)
    if p3.kind is not TaskKind.OUT_OF_DOMAIN:
        fail("fuera dominio", p3.kind.value)
    ok("clima -> fuera de dominio")


def test_memory_store() -> None:
    print("\n[IE3] Memoria de largo plazo")
    store = CaseMemoryStore(base_dir=os.path.join(ROOT, "case_memory", "_test"))
    sid = f"test-{uuid.uuid4().hex[:8]}"
    store.append_fact(sid, "Colaborador preguntó por bono de colación", tema="beneficios")
    store.register_ticket(sid, "INT-99999")
    loaded = store.load(sid)
    if not loaded.facts or "INT-99999" not in loaded.ticket_ids:
        fail("persistencia memoria")
    ok("hechos + tickets persistidos")


def test_agent_offline_turns() -> None:
    print("\n[IE1–IE4] Agente orquestado (MODEL_PROVIDER=local)")
    os.environ["MODEL_PROVIDER"] = "local"
    sid = uuid.uuid4().hex

    turn1 = run_agent("¿Cuál es el bono de colación?", [], sid)
    if not turn1.plan_lines or not turn1.tools_used:
        fail("turno FAQ", "sin plan o tools")
    ok(f"FAQ · tools={','.join(turn1.tools_used[:3])}")

    turn2 = run_agent("¿Mañana va a llover?", [], sid)
    if not has_derivation_phrase(turn2.text):
        fail("clima", "debía derivar")
    ok("fuera de dominio -> derivación")

    history = [
        {"role": "user", "content": "Necesito orientación por acoso en el trabajo"},
        {"role": "assistant", "content": "Te oriento según Ley Karin."},
    ]
    turn3 = run_agent("Quiero abrir un sumario por finiquito litigioso", history, sid)
    if turn3.task_kind != TaskKind.SENSITIVE.value:
        fail("sensible", turn3.task_kind)
    if not turn3.tickets:
        fail("sensible", "debía crear ticket")
    ok(f"caso sensible -> ticket {turn3.tickets[0]['id']}")


def test_live_tool_agent() -> None:
    from src.config import MODEL_PROVIDER

    if MODEL_PROVIDER == "local":
        print("\n[SKIP live] MODEL_PROVIDER=local")
        return
    if MODEL_PROVIDER == "google" and not os.getenv("GOOGLE_API_KEY"):
        print("\n[SKIP live] sin GOOGLE_API_KEY")
        return
    print(f"\n[IE1–IE2] Agente con tools ({MODEL_PROVIDER})")
    sid = uuid.uuid4().hex
    turn = run_agent("¿Cuántos días administrativos pagados tengo?", [], sid)
    if not turn.text:
        fail("respuesta vacía")
    ok(f"respuesta generada · tools={turn.tools_used}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    print("IntegraBot — escenarios agente EP2")
    test_planner()
    test_memory_store()
    test_agent_offline_turns()
    if args.live:
        test_live_tool_agent()
    print("\nEscenarios EP2 completados.\n")


if __name__ == "__main__":
    main()
