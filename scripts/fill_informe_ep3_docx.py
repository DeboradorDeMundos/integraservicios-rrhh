#!/usr/bin/env python
"""Genera el informe EP3 con la misma plantilla Duoc que EP1 y EP2."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(__file__))

import fill_informe_docx as docx_helpers

Document = docx_helpers.Document
TEMPLATE_PATH = os.path.join(ROOT, "_informe_work.docx")
FALLBACK_TEMPLATE = os.path.join(ROOT, "Informe EP1 ISY0101.docx")
DIAGRAM_PATH = os.path.join(ROOT, "docs", "diagrama_observabilidad_ep3.png")
DASHBOARD_PATH = os.path.join(ROOT, "docs", "dashboard_ep3.png")
SUMMARY_PATH = os.path.join(ROOT, "observability", "ep3_summary.json")
BEFORE_PATH = os.path.join(ROOT, "observability", "ep3_summary_antes.json")

OUTPUTS = [
    os.path.join(ROOT, "Informe EP3 ISY0101.docx"),
    os.path.join(ROOT, "Informe EP3 ISY0101_Diego_Madrid.docx"),
    os.path.join(ROOT, "eva3", "Informe_EP3_ISY0101_Diego_Madrid.docx"),
]

add_body = docx_helpers.add_body
add_heading = docx_helpers.add_heading
add_table = docx_helpers.add_table
add_figure = docx_helpers.add_figure
clear_body_after_cover = docx_helpers.clear_body_after_cover
finalize_cover_page_break = docx_helpers.finalize_cover_page_break
set_paragraph_text = docx_helpers.set_paragraph_text
set_run_font = docx_helpers.set_run_font


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _pct(value: float) -> str:
    return f"{float(value) * 100:.0f} %"


def _jaccard(summary: dict, intent: str) -> str:
    for row in summary["metrics"]["consistency_by_intent"]:
        if row["intent"] == intent:
            return _pct(row["jaccard"])
    return "s/d"


def update_cover_ep3(doc) -> None:
    mapping = {
        3: "INGENIERÍA DE SOLUCIONES CON INTELIGENCIA ARTIFICIAL",
        4: "ISY0101 — Sección 011V",
        5: "San Bernardo, Chile",
        10: "IntegraBot — Observabilidad del agente de RRHH (EP3)",
        16: "Integrante:",
        18: "Diego Alejandro Madrid Muñoz",
        19: "RUT: 19.914.672-6",
        23: "Prof. Jaime Andrés Menéndez Silva",
        25: "Evaluación Parcial N°3 — Encargo con Presentación",
        26: "23 de noviembre de 2026",
    }
    for idx, text in mapping.items():
        p = doc.paragraphs[idx]
        set_paragraph_text(p, text, center=True)
        for run in p.runs:
            set_run_font(run, bold=(idx == 10))


def add_index_ep3(doc) -> None:
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.shared import Pt

    p = doc.add_paragraph()
    run = p.add_run("ÍNDICE DE CONTENIDO")
    set_run_font(run, bold=True)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)

    entries = [
        (0, "Introducción"),
        (0, "1. Análisis del caso y continuidad EP1 → EP3"),
        (1, "1.1 Qué se midió sobre el agente ya construido"),
        (0, "2. Métricas de observabilidad (IE1, IE2)"),
        (0, "3. Registros, trazabilidad y cuellos de botella (IE3)"),
        (0, "4. Dashboard de monitoreo (IE4)"),
        (0, "5. Recomendaciones, escala y uso responsable (IE5, IE7, IE8)"),
        (0, "Conclusión"),
        (0, "Reflexión individual"),
        (0, "Declaración de uso de inteligencia artificial"),
        (0, "Bibliografía"),
    ]
    for level, entry in entries:
        docx_helpers.add_index_line(doc, entry, level)

    pb = doc.add_paragraph()
    pb.add_run().add_break(WD_BREAK.PAGE)


def add_bibliography(doc) -> None:
    from docx.enum.text import WD_LINE_SPACING
    from docx.shared import Inches

    add_heading(doc, "Bibliografía")
    refs = [
        "Chroma. (2026). ChromaDB documentation. https://docs.trychroma.com/",
        "Duoc UC. (2025). Uso de inteligencia artificial en el aprendizaje. https://bibliotecas.duoc.cl/ia",
        "Google. (2026). Gemini API documentation. https://ai.google.dev/",
        "LangChain. (2026). LangChain Python documentation. https://python.langchain.com/",
        "Streamlit. (2026). Streamlit documentation. https://docs.streamlit.io/",
    ]
    for ref in refs:
        p = doc.add_paragraph()
        run = p.add_run(ref)
        set_run_font(run)
        pf = p.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        pf.line_spacing = 1.5
        pf.left_indent = Inches(0.5)
        pf.first_line_indent = Inches(-0.5)


def build_content_ep3(doc, after: dict, before: dict) -> None:
    metrics = after["metrics"]
    latency = metrics["latency_ms"]
    warm_mean = (metrics["n"] * latency["mean"] - latency["max"]) / max(metrics["n"] - 1, 1)

    add_index_ep3(doc)

    add_heading(doc, "Introducción")
    add_body(
        doc,
        "El presente informe documenta la Evaluación Parcial N°3 de IntegraBot, el agente de "
        "Gestión de Personas de IntegraServicios S.A. ya construido en la EP1 (RAG con citas) "
        "y en la EP2 (plan, herramientas, memoria y ticket). La EP3 no reemplaza ese sistema: "
        "mide su ejecución. Se implementan métricas de precisión, consistencia, errores, "
        "latencia y uso de recursos, se examinan los registros y se muestra el comportamiento "
        "en un dashboard, con recomendaciones fundadas en esos datos.",
    )
    add_body(
        doc,
        "Repositorio: https://github.com/DeboradorDeMundos/integraservicios-rrhh. "
        "Chat: streamlit run app.py. Dashboard: streamlit run dashboard.py. "
        "Batería: python scripts/observability_eval.py. "
        "Los resultados citados corresponden a observability/ep3_summary.json.",
    )

    add_heading(doc, "1. Análisis del caso y continuidad EP1 → EP3")
    add_body(
        doc,
        "IntegraServicios recibe cerca de 750 consultas mensuales. El límite de negocio sigue "
        "siendo el de las entregas anteriores: responder en menos de 5 segundos y no inventar "
        "montos, plazos ni artículos. La EP3 agrega observabilidad para saber si ese agente "
        "se comporta igual cuando la pregunta cambia de redacción, cuánto tarda, si falla y "
        "cuánta memoria usa, sin convertir el registro en vigilancia del colaborador.",
    )
    add_heading(doc, "1.1 Qué se midió sobre el agente ya construido", level=2)
    add_table(
        doc,
        "Tabla 1. Métricas implementadas (EP3)",
        ["Métrica", "Definición operativa", "Dónde"],
        [
            ["Precisión", "Cita, derivación o ticket según el escenario", "src/observability.py"],
            ["Consistencia", "Jaccard entre paráfrasis de la misma intención", "consistency_by_intent"],
            ["Errores", "Excepciones por turno", "campo error del JSONL"],
            ["Latencia", "P50, P95 y SLO de 5 s, aparte del arranque", "latency_ms"],
            ["Recursos", "CPU del turno y pico de memoria Python", "cpu_ms, peak_kb"],
        ],
    )

    add_heading(doc, "2. Métricas de observabilidad (IE1, IE2)")
    add_body(
        doc,
        "La batería tiene 17 intenciones repetidas dos veces (34 turnos), en modo local. "
        "Cada intención incluye al menos una paráfrasis, de modo que no se evalúa solo la "
        "frase de la demostración. Un turno es preciso si cita cuando la consulta es de "
        "beneficios o de norma, si deriva cuando está fuera de dominio, o si abre un ticket "
        "INT cuando el caso es sensible. El RUT de prueba no se persiste: el JSONL guarda "
        "el marcador [RUT] y la sesión queda como hash.",
    )
    add_table(
        doc,
        "Tabla 2. Resultados de la batería EP3",
        ["Métrica", "Resultado", "Lectura"],
        [
            ["Precisión", _pct(metrics["precision"]), f"{metrics['n_labeled']} turnos etiquetados"],
            ["Consistencia", _pct(metrics["consistency"]), "Jaccard medio entre paráfrasis"],
            ["Errores", _pct(metrics["error_rate"]), f"{metrics['error_count']} excepciones"],
            ["Latencia p50", f"{latency['p50']:.0f} ms", "Turno típico, índice ya cargado"],
            ["Latencia p95", f"{latency['p95']:.0f} ms", "Por debajo del SLO de 5 s"],
            ["Latencia máxima", f"{latency['max']:.0f} ms", "Primer turno: carga de embeddings y Chroma"],
            ["Cumplimiento SLO", _pct(metrics["slo_compliance"]), f"{metrics['slo_breach_count']} turno fuera de límite"],
            ["CPU media", f"{metrics['cpu_ms']['mean']:.0f} ms", "Tiempo de procesador del turno"],
            ["Memoria pico", f"{metrics['peak_kb']['max']:.0f} KB", "Tracemalloc; el máximo es el arranque"],
        ],
    )
    add_table(
        doc,
        "Tabla 3. Precisión por conducta esperada",
        ["Conducta", "Aciertos", "Tasa"],
        [
            ["Cita de beneficio interno", "16/16", "100 %"],
            ["Cita normativa (Karin / horas extra)", "8/8", "100 %"],
            ["Derivación fuera de dominio", "6/6", "100 %"],
            ["Ticket en caso sensible", "4/4", "100 %"],
        ],
    )
    add_body(
        doc,
        "No hubo contradicción de montos entre paráfrasis. La consistencia de Ley Karin pasó "
        f"de {_jaccard(before, 'karin')} en la medición inicial a {_jaccard(after, 'karin')} "
        "después del ajuste. El resto de las intenciones ya estaba en 100 %.",
    )

    add_heading(doc, "3. Registros, trazabilidad y cuellos de botella (IE3)")
    add_body(
        doc,
        f"El primer turno tardó {latency['max'] / 1000:.1f} segundos. La media de los siguientes "
        f"queda en {warm_mean:.0f} ms. Ese salto no es una consulta lenta de un colaborador: es "
        "la carga de sentence-transformers y de ChromaDB. En la interfaz ese costo ya está fuera "
        "de la pregunta, porque Streamlit precarga el agente al abrir la app. El script de batería "
        "medía el arranque dentro del primer turno. Por eso el cumplimiento del SLO de 5 segundos "
        f"es {_pct(metrics['slo_compliance'])} y no 100 %: falla un solo evento, el de partida. "
        f"El percentil 95 ({latency['p95']:.0f} ms) describe las consultas ya tibias.",
    )
    add_body(
        doc,
        "El segundo hallazgo está en Ley Karin. Antes del ajuste, «¿Cómo se denuncia el acoso "
        "laboral?» citaba el RIOHS y «¿Cuál es el canal para denunciar acoso laboral según Ley "
        "Karin?» citaba el Código del Trabajo. El procedimiento era el mismo (denuncia verbal o "
        "escrita, plazo de 30 días y confidencialidad), pero la fuente ganadora cambiaba. La "
        "corrección está en el generador local: si la pregunta menciona Karin o acoso, el "
        "fragmento del Código del Trabajo recibe prioridad de desempate. No se inventa texto; "
        "se fija qué documento manda cuando hay dos bloques válidos.",
    )
    add_body(
        doc,
        "El registro también separa los caminos que no deben consultar el corpus. Clima y fútbol "
        "derivan sin cita. Finiquito litigioso y cheque litigioso abren ticket INT. Cada evento "
        "guarda plan, herramientas, citas y fase cold_start o warm.",
    )
    add_figure(
        doc,
        DIAGRAM_PATH,
        "Figura 1. Flujo de observabilidad de IntegraBot (EP3).",
        width=docx_helpers.Inches(5.8),
    )

    add_heading(doc, "4. Dashboard de monitoreo (IE4)")
    add_body(
        doc,
        "El monitoreo está en dashboard.py y se abre con streamlit run dashboard.py. Muestra "
        "precisión, consistencia, errores, latencia p95 y cumplimiento del SLO, la latencia "
        "turno a turno, la media por tipo de tarea en turnos ya tibios y la consistencia por "
        "intención. El gráfico de la serie conserva el pico de arranque; las medias por tarea "
        "no lo incluyen, para no hacer ver lenta una consulta de beneficios que en régimen "
        "tarda menos de un segundo. Cada fila se puede abrir: plan, herramientas, citas y ticket. "
        "El chat en vivo escribe observability/runs.jsonl y se suma al panel con Actualizar.",
    )
    add_figure(
        doc,
        DASHBOARD_PATH,
        "Figura 2. Dashboard de la batería EP3: precisión 100 %, consistencia 100 %, errores 0 %, p95 145 ms.",
        width=docx_helpers.Inches(5.8),
    )

    add_heading(doc, "5. Recomendaciones, escala y uso responsable (IE5, IE7, IE8)")
    add_table(
        doc,
        "Tabla 4. Decisiones a partir de los registros",
        ["Decisión", "Motivo observado"],
        [
            ["SLO solo en turnos tibios", "El arranque (12,6 s) no es una consulta de colaborador"],
            ["Desempate de cita Ley Karin", "Dos paráfrasis válidas citaban PDFs distintos"],
            ["Media por tipo de tarea", "Un sensible abre ticket; un fuera de dominio no debe pagar RAG"],
            ["Telemetría sin RUT ni correo", "El JSONL no es el expediente; el ticket de RRHH sí puede llevar el RUT"],
            ["Escalamiento humano", "Acoso, finiquito y sumario siguen yendo a una persona"],
        ],
    )
    add_body(
        doc,
        "En producción el mismo diseño publica tasas y latencias, no el texto completo de la "
        "consulta, y no reenvía el registro a un tercero. Los PDF del repositorio son material "
        "de la evaluación y no reemplazan el Código del Trabajo ni los instrumentos reales de "
        "la empresa. Para escalar, la precarga del índice queda al levantar el servicio y el "
        "SLO se cobra a la pregunta, no al arranque.",
    )

    add_heading(doc, "Conclusión")
    add_body(
        doc,
        "Con la Evaluación Parcial N°3, IntegraBot pasa de ser un agente que responde y registra "
        "tickets a un agente cuya ejecución se puede medir. En 34 turnos con redacción variable "
        f"la conducta esperada se cumplió en el {_pct(metrics['precision'])}, no hubo excepciones "
        f"y la consistencia quedó en {_pct(metrics['consistency'])} después de fijar la cita de "
        "Ley Karin. El único quiebre del límite de 5 segundos es el arranque del índice. Se "
        "conservan los guardrails de la EP1 y la orquestación de la EP2, y se agrega un registro "
        "local sin datos personales, visible en el dashboard para la defensa.",
    )

    add_heading(doc, "Reflexión individual", level=2)
    add_body(
        doc,
        "Diego Alejandro Madrid Muñoz: En la EP3 seguí con el agente que ya tenía y le puse "
        "medición. Escribí src/observability.py para guardar un evento por turno, "
        "scripts/observability_eval.py para repetir las preguntas con otra redacción, y "
        "dashboard.py para ver precisión, latencia, consistencia, errores y memoria. Lo que "
        "más me costó fue el primer número que se veía bien: el p95 daba cerca de 145 ms, pero "
        "el primer turno se iba a más de 12 segundos porque ahí se carga el índice. Si hubiera "
        "mostrado solo el promedio, el límite de 5 segundos parecía casi cumplido y el problema "
        "real quedaba escondido. El otro hallazgo salió al comparar los logs de Ley Karin: una "
        "redacción citaba el RIOHS y la otra el Código del Trabajo, con el mismo procedimiento. "
        "Ajusté el desempate en local_generator.py y, al volver a correr la batería, la "
        "consistencia de esa intención pasó de 84 % a 100 %. También probé una consulta de "
        "colación con un RUT y en el archivo quedó [RUT], no el número. Aprendí que en Gestión "
        "de Personas observar sirve cuando el registro obliga a corregir algo concreto, no "
        "cuando el gráfico se ve ordenado.",
    )

    add_heading(doc, "Declaración de uso de inteligencia artificial", level=2)
    add_body(
        doc,
        "Se empleó IA generativa (Cursor IDE) como apoyo en revisión de código, borrador de "
        "documentación, diagramas y presentación HTML. El análisis del caso, las decisiones de "
        "diseño, las conclusiones y la reflexión individual fueron elaborados y revisados por "
        "el autor. Referencia institucional: Duoc UC (2025), https://bibliotecas.duoc.cl/ia.",
    )

    add_bibliography(doc)


def main() -> None:
    source = TEMPLATE_PATH if os.path.isfile(TEMPLATE_PATH) else FALLBACK_TEMPLATE
    if not os.path.isfile(source):
        print(f"No hay plantilla Word: {source}", file=sys.stderr)
        raise SystemExit(1)
    if not os.path.isfile(SUMMARY_PATH) or not os.path.isfile(BEFORE_PATH):
        print("Faltan observability/ep3_summary.json o ep3_summary_antes.json", file=sys.stderr)
        raise SystemExit(1)

    after = _load(SUMMARY_PATH)
    before = _load(BEFORE_PATH)
    doc = Document(source)
    update_cover_ep3(doc)
    finalize_cover_page_break(doc)
    clear_body_after_cover(doc)
    build_content_ep3(doc, after, before)

    for path in OUTPUTS:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            doc.save(path)
            print(f"Informe EP3 generado: {path}")
        except PermissionError:
            alt = path.replace(".docx", "_corregido.docx")
            doc.save(alt)
            print(f"Cierra Word. Guardado en: {alt}", file=sys.stderr)


if __name__ == "__main__":
    main()
