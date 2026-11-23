#!/usr/bin/env python
"""Genera Informe EP2 ISY0101.docx (agente funcional IntegraBot)."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(__file__))

import fill_informe_docx as docx_helpers

Document = docx_helpers.Document
DOC_PATH = os.path.join(ROOT, "Informe EP2 ISY0101.docx")
TEMPLATE_PATH = os.path.join(ROOT, "_informe_work.docx")
FALLBACK_TEMPLATE = os.path.join(ROOT, "Informe EP1 ISY0101.docx")
DIAGRAM_PATH = os.path.join(ROOT, "docs", "diagrama_orquestacion_ep2.png")
COVER_PARAGRAPHS = docx_helpers.COVER_PARAGRAPHS

add_body = docx_helpers.add_body
add_heading = docx_helpers.add_heading
add_table = docx_helpers.add_table
add_figure = docx_helpers.add_figure
clear_body_after_cover = docx_helpers.clear_body_after_cover
finalize_cover_page_break = docx_helpers.finalize_cover_page_break
set_paragraph_text = docx_helpers.set_paragraph_text
set_run_font = docx_helpers.set_run_font

CONCLUSION_EP2 = (
    "Con la Evaluación Parcial N°2, IntegraBot deja de ser únicamente un copiloto que "
    "responde citando PDFs y pasa a actuar como un asistente de Gestión de Personas con "
    "pasos visibles: clasifica la consulta, elige si busca en reglamento interno o en "
    "normativa externa, mantiene memoria de la conversación y, cuando corresponde, registra "
    "un ticket INT para escalamiento. Para IntegraServicios S.A. esto apunta a aliviar "
    "consultas repetitivas sin relajar el cumplimiento: se conservan los guardrails y las "
    "citas del EP1, sumando autonomía controlada en flujos multietapa y en casos sensibles. "
    "Los indicadores IE1 a IE6 quedan respaldados en código, diagrama, README y pruebas "
    "automatizadas del repositorio GitHub."
)

REFLEXION_EP2 = (
    "Diego Alejandro Madrid Muñoz: En esta entrega extendí el trabajo de la EP1 hacia el "
    "agente: implementé planner.py, memory.py, agent_tools.py y la conexión en app.py, "
    "incluyendo el expander de orquestación para que el docente vea plan y herramientas "
    "en la demo. Lo que más me complicó fue equilibrar la cuota de la API de Gemini con "
    "pruebas en vivo — tuve que usar modo local en algunos ensayos — y corregir "
    "comportamientos raros, como un seguimiento de ticket que terminaba buscando en el RAG "
    "en lugar de leer la memoria del caso. También afiné el manejo de consultas sensibles "
    "(finiquito o cheque litigioso) para que abran ticket sin inventar montos. Aprendí que "
    "en RRHH un agente no gana por sonar más «inteligente», sino por ser trazable y "
    "prudente; por eso prioricé scripts de prueba y una demo estable para la presentación."
)


def update_cover_ep2(doc) -> None:
    mapping = {
        3: "INGENIERÍA DE SOLUCIONES CON INTELIGENCIA ARTIFICIAL",
        4: "ISY0101 — Sección 011V",
        5: "San Bernardo, Chile",
        10: "IntegraBot — Agente funcional de RRHH (EP2)",
        16: "Integrante:",
        18: "Diego Alejandro Madrid Muñoz",
        19: "RUT: 19.914.672-6",
        23: "Prof. Jaime Andrés Menéndez Silva",
        25: "Evaluación Parcial N°2 — Encargo con Presentación",
        26: "17 de octubre de 2026",
    }
    for idx, text in mapping.items():
        p = doc.paragraphs[idx]
        set_paragraph_text(p, text, center=True)
        for run in p.runs:
            set_run_font(run, bold=(idx == 10))


def add_index_ep2(doc) -> None:
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
    from docx.shared import Pt

    p = doc.add_paragraph()
    run = p.add_run("ÍNDICE DE CONTENIDO")
    set_run_font(run, bold=True)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)

    entries = [
        (0, "Introducción"),
        (0, "1. Análisis del caso y continuidad EP1 → EP2"),
        (1, "1.1 Objetivos y corpus documental"),
        (0, "2. Herramientas y framework del agente (IE1, IE2)"),
        (0, "3. Memoria y recuperación semántica (IE3, IE4)"),
        (0, "4. Planificación y decisiones adaptativas (IE5)"),
        (0, "5. Orquestación, pruebas y limitaciones (IE6, IE8)"),
        (0, "6. Justificación de componentes (IE9)"),
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
    from docx.shared import Inches, Pt

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


def build_content_ep2(doc) -> None:
    add_index_ep2(doc)

    add_heading(doc, "Introducción")
    add_body(
        doc,
        "El presente informe documenta la evolución de IntegraBot — desarrollado en la "
        "Evaluación Parcial N°1 como copiloto RAG — hacia un agente funcional para el área "
        "de Gestión de Personas de IntegraServicios S.A. La EP2 exige herramientas de "
        "consulta y escritura, memoria de corto y largo plazo, planificación ante consultas "
        "multietapa y evidencias técnicas con diagramas y pruebas reproducibles en GitHub.",
    )
    add_body(
        doc,
        "Repositorio: https://github.com/DeboradorDeMundos/integraservicios-rrhh. "
        "Ejecución: python generate_data.py && streamlit run app.py. "
        "Pruebas: python scripts/agent_scenarios_test.py [--live] y scripts/smoke_test.py.",
    )

    add_heading(doc, "1. Análisis del caso y continuidad EP1 → EP2")
    add_body(
        doc,
        "IntegraServicios recibe cerca de 750 consultas mensuales sobre beneficios, permisos "
        "y normativa laboral. En la EP1 se resolvió la lectura documental con RAG; en la EP2 "
        "se añade capacidad de decidir acciones (buscar, recordar, registrar ticket) sin "
        "perder trazabilidad ni las reglas anti-alucinación ya implementadas.",
    )
    add_heading(doc, "1.1 Objetivos y corpus documental", level=2)
    add_table(
        doc,
        "Tabla 1. Objetivos de intervención (EP2)",
        ["Objetivo", "Meta"],
        [
            ["Autonomía controlada", "Elegir búsqueda, memoria o ticket según el caso"],
            ["Continuidad conversacional", "Memoria corta (historial) y larga (caso por sesión)"],
            ["Trazabilidad", "Plan, herramientas, fuentes RAG y ticket INT visibles en UI"],
            ["Herencia EP1", "Corpus dual, MMR k=4 y guardrails.py"],
        ],
    )
    add_table(
        doc,
        "Tabla 2. Corpus dual indexado",
        ["Tipo", "Documento", "Herramienta"],
        [
            ["Interno", "RIOHS_IntegraServicios_2026.pdf", "buscar_politicas_internas"],
            ["Interno", "Contrato_Colectivo_2026.pdf", "buscar_politicas_internas"],
            ["Externo", "Codigo_del_Trabajo_Chile.pdf", "buscar_normativa_externa"],
        ],
    )

    add_heading(doc, "2. Herramientas y framework del agente (IE1, IE2)")
    add_body(
        doc,
        "El agente usa LangChain (mensajes, tools, bind_tools) y un bucle ReAct de hasta "
        "cuatro iteraciones en src/agent.py. Cuatro herramientas cubren consulta documental "
        "filtrada por corpus, persistencia de memoria de caso y tickets RRHH mock con formato "
        "INT-xxxxx. El stack complementario incluye planner.py, retriever.py, rag_engine.py "
        "y Streamlit (app.py) con expander «Orquestación del agente».",
    )
    add_table(
        doc,
        "Tabla 3. Herramientas del agente",
        ["Herramienta", "Tipo", "Función"],
        [
            ["buscar_politicas_internas", "Consulta", "RIOHS + Contrato (filtro interno)"],
            ["buscar_normativa_externa", "Consulta", "Código del Trabajo / Ley Karin (externo)"],
            ["guardar_memoria_caso", "Escritura", "Hechos y tema en case_memory por sesión"],
            ["registrar_ticket_gestion_personas", "Escritura", "Ticket en tickets_local (mock INT)"],
        ],
    )

    add_heading(doc, "3. Memoria y recuperación semántica (IE3, IE4)")
    add_body(
        doc,
        "La memoria de corto plazo inyecta hasta ocho turnos vía conversation.py "
        "(AGENT_HISTORY_LIMIT). La memoria de largo plazo (memory.py) guarda colaborador, "
        "tema, hechos y tickets asociados al session_id de Streamlit, lo que permite "
        "follow-ups como el estado de un ticket abierto en la misma sesión.",
    )
    add_table(
        doc,
        "Tabla 4. Memoria, recuperación y parámetros RAG",
        ["Componente", "Implementación", "Parámetro / rol"],
        [
            ["Corto plazo", "conversation.py", "8 turnos en prompt"],
            ["Largo plazo", "memory.py", "JSON por session_id"],
            ["Retriever", "ChromaDB + MMR", "k=4, lambda_mult=0.75"],
            ["Filtro corpus", "metadata source_type", "Separar interno / externo"],
        ],
    )

    add_heading(doc, "4. Planificación y decisiones adaptativas (IE5)")
    add_body(
        doc,
        "src/planner.py clasifica cada consulta (FAQ, multietapa, sensible, fuera de dominio, "
        "seguimiento) y entrega un plan numerado inyectado al system prompt. La clasificación "
        "se refleja en la interfaz para la defensa oral y el video de la evaluación.",
    )
    add_table(
        doc,
        "Tabla 5. Casos de demostración representativos",
        ["Consulta / escenario", "Plan", "Resultado esperado"],
        [
            ["Bono de colación", "FAQ", "Monto + cita documental"],
            ["Días administrativos y documentos", "Multietapa", "Síntesis + memoria de caso"],
            ["¿Mañana va a llover?", "Fuera de dominio", "Derivación sin inventar"],
            ["Finiquito o cheque litigioso", "Sensible", "Ticket INT + escalamiento RRHH"],
            ["Estado del ticket abierto", "Seguimiento", "Memoria + estado del ticket"],
        ],
    )

    add_heading(doc, "5. Orquestación, pruebas y limitaciones (IE6, IE8)")
    add_body(
        doc,
        "El flujo app.py → run_agent → planner → tools → RAG/guardrails entrega respuesta "
        "con trazabilidad. scripts/agent_scenarios_test.py valida planificación, memoria y "
        "modos sensible/seguimiento; scripts/smoke_test.py mantiene regresión del corpus EP1.",
    )
    add_table(
        doc,
        "Tabla 6. Módulos principales y pruebas",
        ["Elemento", "Responsabilidad / uso"],
        [
            ["agent.py, agent_tools.py", "Bucle ReAct y herramientas LangChain"],
            ["planner.py, memory.py", "Planificación y continuidad de caso"],
            ["retriever.py, guardrails.py", "Recuperación MMR y validación post-LLM"],
            ["agent_scenarios_test.py", "Pruebas offline/ --live de escenarios EP2"],
            ["smoke_test.py", "Regresión RAG EP1"],
        ],
    )
    add_figure(
        doc,
        DIAGRAM_PATH,
        "Figura 1. Diagrama de orquestación del agente IntegraBot (EP2).",
        width=docx_helpers.Inches(5.8),
    )
    add_body(
        doc,
        "Limitaciones: PDF simulados para la evaluación, tickets mock, sin SSO ni portal "
        "RRHH productivo, y dependencia de cuota API (mitigada con MODEL_PROVIDER local o "
        "Groq en demos). IntegraBot no reemplaza asesoría legal ni investigaciones Ley Karin.",
    )

    add_heading(doc, "6. Justificación de componentes (IE9)")
    add_table(
        doc,
        "Tabla 7. Decisiones de diseño",
        ["Decisión", "Motivo"],
        [
            ["ReAct + tools", "EP2 exige autonomía con consulta y escritura auditables"],
            ["Dos retrievers filtrados", "Evitar mezclar reglamento interno y ley externa"],
            ["Memoria JSON por sesión", "Multietapa sin inflar tokens del prompt"],
            ["Tickets mock INT", "Evidencia de escritura reproducible en demo"],
            ["Guardrails EP1", "Mismo rigor legal con agente más complejo"],
        ],
    )

    add_heading(doc, "Conclusión")
    add_body(doc, CONCLUSION_EP2)

    add_heading(doc, "Reflexión individual", level=2)
    add_body(doc, REFLEXION_EP2)

    add_heading(doc, "Declaración de uso de inteligencia artificial", level=2)
    add_body(
        doc,
        "Se empleó IA generativa (Cursor IDE, Google Gemini API) como apoyo en revisión de "
        "código, borrador de documentación, diagramas y presentación HTML. El análisis del "
        "caso, las decisiones de diseño, las conclusiones y la reflexión individual fueron "
        "elaborados y revisados por el autor. Referencia institucional: Duoc UC (2025), "
        "https://bibliotecas.duoc.cl/ia.",
    )

    add_bibliography(doc)


def main() -> None:
    diagram_script = os.path.join(ROOT, "scripts", "render_diagram_ep2.py")
    if os.path.isfile(diagram_script):
        import subprocess

        subprocess.run([sys.executable, diagram_script], check=False)

    source = TEMPLATE_PATH if os.path.isfile(TEMPLATE_PATH) else FALLBACK_TEMPLATE
    if not os.path.isfile(source):
        print(f"No hay plantilla Word: {source}", file=sys.stderr)
        raise SystemExit(1)

    doc = Document(source)
    update_cover_ep2(doc)
    finalize_cover_page_break(doc)
    clear_body_after_cover(doc)
    build_content_ep2(doc)
    try:
        doc.save(DOC_PATH)
        print(f"Informe EP2 generado: {DOC_PATH}")
    except PermissionError:
        alt = os.path.join(ROOT, "Informe EP2 ISY0101_corregido.docx")
        doc.save(alt)
        print(f"Cierra Word. Guardado en: {alt}", file=sys.stderr)


if __name__ == "__main__":
    main()
