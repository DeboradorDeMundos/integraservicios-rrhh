#!/usr/bin/env python
"""Genera docs/diagrama_orquestacion_ep2.png (figura informe EP2)."""
from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs")
OUT_PATH = os.path.join(OUT_DIR, "diagrama_orquestacion_ep2.png")


def main() -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise SystemExit("pip install pillow")

    os.makedirs(OUT_DIR, exist_ok=True)
    w, h = 1200, 640
    img = Image.new("RGB", (w, h), "#F4F7FC")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
        font_sm = ImageFont.truetype("arial.ttf", 14)
        font_title = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font = font_sm = font_title = ImageFont.load_default()

    draw.rounded_rectangle((24, 24, w - 24, h - 24), radius=16, outline="#0B5CAB", width=3, fill="#FFFFFF")
    draw.text((40, 36), "IntegraBot EP2 — Orquestación del agente", fill="#071A30", font=font_title)

    boxes = [
        (60, 120, 220, 200, "Streamlit\napp.py", "#0B5CAB"),
        (260, 120, 420, 200, "run_agent\nagent.py", "#1A7AD4"),
        (460, 120, 620, 200, "planner.py\nplan + prioridad", "#553C9A"),
        (660, 120, 820, 200, "Memoria corta\nconversation.py", "#276749"),
        (860, 120, 1020, 200, "Memoria larga\nmemory.py", "#276749"),
        (160, 280, 340, 360, "buscar_politicas_internas", "#C05621"),
        (380, 280, 560, 360, "buscar_normativa_externa", "#C05621"),
        (600, 280, 780, 360, "guardar_memoria_caso", "#9A3412"),
        (820, 280, 1000, 360, "registrar_ticket_rrhh", "#9A3412"),
        (300, 440, 500, 520, "ChromaDB MMR\nretriever.py", "#0B5CAB"),
        (540, 440, 740, 520, "RAG + guardrails\nrag_engine.py", "#1A7AD4"),
        (780, 440, 980, 520, "tickets_local/\ncase_memory/", "#276749"),
    ]
    for x1, y1, x2, y2, label, color in boxes:
        draw.rounded_rectangle((x1, y1, x2, y2), radius=10, fill=color, outline="#071A30")
        draw.multiline_text((x1 + 12, y1 + 16), label, fill="#FFFFFF", font=font_sm, spacing=4)

    arrows = [
        ((140, 200), (140, 280)),
        ((340, 200), (340, 280)),
        ((540, 200), (540, 280)),
        ((740, 200), (740, 280)),
        ((940, 200), (940, 280)),
        ((250, 320), (300, 480)),
        ((470, 320), (400, 440)),
        ((690, 320), (620, 440)),
        ((910, 320), (880, 440)),
        ((500, 480), (540, 480)),
        ((740, 480), (780, 480)),
    ]
    for (x1, y1), (x2, y2) in arrows:
        draw.line((x1, y1, x2, y2), fill="#071A30", width=2)

    draw.text((40, 560), "LangChain bind_tools (ReAct) · IE1–IE2 · Consulta + Escritura + Planificación", fill="#071A30", font=font)
    img.save(OUT_PATH)
    print(f"Diagrama guardado: {OUT_PATH}")


if __name__ == "__main__":
    main()
