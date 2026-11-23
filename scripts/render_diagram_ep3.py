#!/usr/bin/env python
"""Genera docs/diagrama_observabilidad_ep3.png."""
from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "docs", "diagrama_observabilidad_ep3.png")


def main() -> None:
    from PIL import Image, ImageDraw, ImageFont

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    w, h = 1400, 760
    img = Image.new("RGB", (w, h), "#F4F7FB")
    draw = ImageDraw.Draw(img)
    try:
        title = ImageFont.truetype("arial.ttf", 28)
        font = ImageFont.truetype("arial.ttf", 18)
        small = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        title = font = small = ImageFont.load_default()

    draw.rounded_rectangle((20, 20, w - 20, h - 20), radius=18, outline="#0B5CAB", width=3, fill="#FFFFFF")
    draw.text((48, 40), "IntegraBot EP3 — Observabilidad del agente", fill="#071A30", font=title)

    boxes = [
        (48, 110, 250, 210, "Colaborador\napp.py", "#0B5CAB"),
        (300, 110, 530, 210, "run_agent\ntraza por turno", "#1A7AD4"),
        (580, 110, 860, 210, "Agente EP2\nplan + tools + RAG", "#553C9A"),
        (910, 110, 1180, 210, "Guardrails\ncita o derivación", "#276749"),
        (160, 300, 460, 420, "observability/*.jsonl\nsin RUT ni correo", "#9A3412"),
        (520, 300, 860, 420, "Métricas\nprecisión · latencia\nconsistencia · errores · RAM", "#C05621"),
        (920, 300, 1240, 420, "dashboard.py\nStreamlit", "#0B5CAB"),
        (300, 520, 620, 640, "Hallazgos\narranque en frío\ncita Ley Karin", "#071A30"),
        (700, 520, 1100, 640, "Recomendaciones\nSLO tibio · privacidad · escala", "#0B5CAB"),
    ]
    for x1, y1, x2, y2, label, color in boxes:
        draw.rounded_rectangle((x1, y1, x2, y2), radius=12, fill=color)
        draw.multiline_text((x1 + 16, y1 + 22), label, fill="#FFFFFF", font=small, spacing=4)

    arrows = [
        (250, 160, 300, 160),
        (530, 160, 580, 160),
        (860, 160, 910, 160),
        (415, 210, 310, 300),
        (720, 210, 690, 300),
        (460, 360, 520, 360),
        (860, 360, 920, 360),
        (690, 420, 460, 520),
        (790, 420, 900, 520),
    ]
    for x1, y1, x2, y2 in arrows:
        draw.line((x1, y1, x2, y2), fill="#071A30", width=3)

    draw.text(
        (48, 690),
        "Cada turno mide latencia, CPU, memoria, herramientas y resultado. El dashboard lee el JSONL local.",
        fill="#334155",
        font=font,
    )
    img.save(OUT_PATH)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
