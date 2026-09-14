#!/usr/bin/env python
"""
Validación del pipeline IntegraBot (rúbrica IE1–IE4).

Uso:
    python scripts/smoke_test.py          # pruebas offline (sin API)
    python scripts/smoke_test.py --live   # incluye consultas reales a Gemini
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from dotenv import load_dotenv

load_dotenv()

from src.config import CORPUS, DATA_DIRECTORY, DEMO_QUESTIONS, ORG_CASE, SourceType
from src.conversation import format_chat_history
from src.guardrails import apply_response_guardrails, extract_citations, has_derivation_phrase


def ok(label: str) -> None:
    print(f"  OK  {label}")


def fail(label: str, detail: str = "") -> None:
    print(f"  FAIL {label}" + (f": {detail}" if detail else ""))
    raise SystemExit(1)


def test_org_case() -> None:
    print("\n[IE1] Caso organizacional")
    assert ORG_CASE.company == "IntegraServicios S.A."
    assert ORG_CASE.monthly_tickets == 750
    ok(f"{ORG_CASE.product} · {ORG_CASE.area} · {ORG_CASE.monthly_tickets} tickets/mes")


def test_corpus_files() -> None:
    print("\n[IE3] Corpus dual interno/externo")
    if not os.path.isdir(DATA_DIRECTORY):
        fail("carpeta data/", "ejecuta python generate_data.py")
    for filename, source_type in CORPUS.items():
        path = os.path.join(DATA_DIRECTORY, filename)
        if not os.path.isfile(path):
            fail(filename, "no encontrado")
        ok(f"{filename} -> {source_type.value}")
    internal = sum(1 for t in CORPUS.values() if t == SourceType.INTERNAL)
    external = sum(1 for t in CORPUS.values() if t == SourceType.EXTERNAL)
    if internal < 2 or external < 1:
        fail("balance corpus", "se requieren ≥2 internos y ≥1 externo")


def test_ingestion_metadata() -> None:
    print("\n[IE3] Metadata source_type en chunks")
    from src.ingestion import load_and_chunk_documents

    chunks = load_and_chunk_documents()
    if not chunks:
        fail("chunking", "sin fragmentos")
    typed = {c.metadata.get("source_type") for c in chunks}
    if "interno" not in typed or "externo" not in typed:
        fail("source_type", f"tipos encontrados: {typed}")
    ok(f"{len(chunks)} fragmentos con etiquetas interno/externo")


def test_conversation_context() -> None:
    print("\n[IE4] Historial conversacional acotado")
    messages = [
        {"role": "user", "content": "¿Cuál es el bono de colación?"},
        {"role": "assistant", "content": "Son $85.000 [Fuente: Contrato_Colectivo_2026.pdf, Cláusula 5]"},
        {"role": "user", "content": "¿Y el aguinaldo de Fiestas Patrias?"},
    ]
    history = format_chat_history(messages, max_turns=2)
    if "Trabajador:" not in history or "IntegraBot:" not in history:
        fail("format_chat_history")
    ok("historial formateado para inyección en prompt")


def test_guardrails() -> None:
    print("\n[IE2] Guardrails post-respuesta")
    empty = apply_response_guardrails("")
    if not has_derivation_phrase(empty):
        fail("respuesta vacía -> derivación")
    ok("respuesta vacía fuerza derivación institucional")
    cited = apply_response_guardrails(
        "El bono es $85.000 [Fuente: Contrato_Colectivo_2026.pdf, Cláusula 5]"
    )
    if not extract_citations(cited):
        fail("citas detectadas")
    ok("respuesta con cita se preserva")


def test_live_pipeline() -> None:
    print("\n[IE3–IE4] Consultas en vivo (Gemini + ChromaDB)")
    if not os.getenv("GOOGLE_API_KEY"):
        print("  SKIP (sin GOOGLE_API_KEY en .env)")
        return

    from src.rag_engine import get_rag_chain

    pipeline = get_rag_chain()
    history = ""

    for question in DEMO_QUESTIONS:
        answer, docs = pipeline.query(question, chat_history=history)
        sources = {os.path.basename(d.metadata.get("source", "")) for d in docs}
        print(f"\n  Q: {question}")
        print(f"  Fragmentos: {len(docs)} | PDFs: {', '.join(sorted(sources)) or '-'}")
        if "llover" in question.lower():
            if not has_derivation_phrase(answer):
                fail(question, "debía derivar, no inventar")
            ok("pregunta fuera de dominio -> derivación")
        elif not extract_citations(answer) and not has_derivation_phrase(answer):
            fail(question, "sin cita ni derivación")
        else:
            ok("respuesta con evidencia o derivación")

        history = format_chat_history(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ]
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke tests IntegraBot")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Ejecuta consultas reales contra Gemini (requiere GOOGLE_API_KEY)",
    )
    args = parser.parse_args()

    print("IntegraBot - smoke tests (codigo / rubrica IE1-IE4)")
    test_org_case()
    test_corpus_files()
    test_ingestion_metadata()
    test_conversation_context()
    test_guardrails()
    if args.live:
        test_live_pipeline()
    else:
        print("\n[INFO] Modo offline. Usa --live para probar consultas con Gemini.")
    print("\nTodos los checks offline pasaron.\n")


if __name__ == "__main__":
    main()
