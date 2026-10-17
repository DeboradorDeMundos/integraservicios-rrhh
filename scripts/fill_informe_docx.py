#!/usr/bin/env python
"""Completa Informe EP1 ISY0101.docx con contenido IntegraBot y formato Duoc."""
from __future__ import annotations

import os
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_PATH = os.path.join(ROOT, "Informe EP1 ISY0101.docx")
TEMPLATE_PATH = os.path.join(ROOT, "_informe_work.docx")
DIAGRAM_PATH = os.path.join(ROOT, "docs", "diagrama_arquitectura_integrabot.png")
COVER_PARAGRAPHS = 28
FONT = "Times New Roman"
BODY_SIZE = Pt(12)


def delete_paragraph(paragraph) -> None:
    element = paragraph._element
    element.getparent().remove(element)


def set_run_font(run, bold: bool = False, italic: bool = False, size=BODY_SIZE) -> None:
    run.font.name = FONT
    run._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    run.font.size = size
    run.font.bold = bold
    run.font.italic = italic


def format_body(paragraph, justify: bool = True, indent: bool = True) -> None:
    pf = paragraph.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.5
    pf.space_after = Pt(0)
    pf.space_before = Pt(0)
    if justify:
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent:
        pf.first_line_indent = Inches(0.5)


def set_paragraph_text(paragraph, text: str, *, bold: bool = False, center: bool = False) -> None:
    paragraph.clear()
    run = paragraph.add_run(text)
    set_run_font(run, bold=bold)
    if center:
        paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        format_body(paragraph)


def add_heading(doc: Document, text: str, level: int = 1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.clear()
    run = p.add_run(text)
    set_run_font(run, bold=True)
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.5
    pf.space_before = Pt(12 if level == 1 else 6)
    pf.space_after = Pt(6)
    pf.first_line_indent = Inches(0)
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p


def add_body(doc: Document, text: str):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run_font(run)
    format_body(p)
    return p


def add_bullet(doc: Document, text: str):
    p = doc.add_paragraph()
    run = p.add_run(f"• {text}")
    set_run_font(run)
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.5
    pf.left_indent = Inches(0.35)
    pf.first_line_indent = Inches(0)
    return p


def add_table(doc: Document, title: str, headers: list[str], rows: list[list[str]]):
    add_body(doc, title)
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    try:
        table.style = "Table Grid"
    except KeyError:
        pass
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        for p in hdr[i].paragraphs:
            for r in p.runs:
                set_run_font(r, bold=True)
    for ri, row in enumerate(rows, start=1):
        for ci, val in enumerate(row):
            table.rows[ri].cells[ci].text = val
            for p in table.rows[ri].cells[ci].paragraphs:
                for r in p.runs:
                    set_run_font(r)
    doc.add_paragraph()


def update_cover(doc: Document) -> None:
    mapping = {
        3: "INGENIERÍA DE SOLUCIONES CON INTELIGENCIA ARTIFICIAL",
        4: "ISY0101 — Sección 011V",
        5: "San Bernardo, Chile",
        10: "IntegraBot — Copiloto RAG de RRHH y Cumplimiento Laboral",
        16: "Integrante:",
        18: "Diego Alejandro Madrid Muñoz",
        19: "RUT: 19.914.672-6",
        23: "Prof. Jaime Andrés Menéndez Silva",
        25: "Evaluación Parcial N°1 — Encargo con Presentación",
        26: "14 de septiembre de 2026",
    }
    for idx, text in mapping.items():
        p = doc.paragraphs[idx]
        set_paragraph_text(p, text, center=True)
        for run in p.runs:
            set_run_font(run, bold=(idx == 10))


def clear_body_after_cover(doc: Document, cover_paragraphs: int = COVER_PARAGRAPHS) -> None:
    """Elimina párrafos Y tablas tras la portada (evita tablas duplicadas al regenerar)."""
    body = doc.element.body
    para_count = 0
    to_remove = []
    for child in list(body):
        if child.tag == qn("w:sectPr"):
            continue
        if child.tag == qn("w:p"):
            para_count += 1
            if para_count > cover_paragraphs:
                to_remove.append(child)
        elif para_count >= cover_paragraphs:
            to_remove.append(child)
    for element in to_remove:
        body.remove(element)


def add_page_break(doc: Document) -> None:
    p = doc.add_paragraph()
    run = p.add_run()
    run.add_break(WD_BREAK.PAGE)


def finalize_cover_page_break(doc: Document) -> None:
    """Un solo salto de página al final de la portada."""
    while len(doc.paragraphs) > COVER_PARAGRAPHS:
        delete_paragraph(doc.paragraphs[COVER_PARAGRAPHS])
    p = doc.paragraphs[COVER_PARAGRAPHS - 1]
    p.clear()
    run = p.add_run()
    run.add_break(WD_BREAK.PAGE)


def add_index_line(doc: Document, text: str, level: int = 0) -> None:
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run_font(run)
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.5
    pf.left_indent = Inches(0.25 * level)
    pf.first_line_indent = Inches(0)
    pf.space_after = Pt(2)


def add_index_page(doc: Document) -> None:
    """Índice manual único (sin campo TOC que arrastraba títulos viejos de la plantilla)."""
    p = doc.add_paragraph()
    run = p.add_run("ÍNDICE DE CONTENIDO")
    set_run_font(run, bold=True)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)

    entries = [
        (0, "Introducción"),
        (0, "1. Análisis del caso organizacional (IE1)"),
        (1, "1.1 Datos disponibles y restricciones"),
        (0, "2. Formulación de prompts (IE2)"),
        (0, "3. Pipeline RAG dual (IE3)"),
        (0, "4. Arquitectura de la solución (IE4)"),
        (0, "5. Pruebas, limitaciones y repositorio (IE5)"),
        (0, "Conclusión"),
        (0, "Reflexión individual"),
        (0, "Declaración de uso de inteligencia artificial"),
        (0, "Bibliografía"),
    ]
    for level, entry in entries:
        add_index_line(doc, entry, level)

    add_page_break(doc)


def add_figure(doc: Document, image_path: str, caption: str, width=Inches(6.2)) -> None:
    if not os.path.isfile(image_path):
        add_body(doc, f"[Figura no encontrada: {image_path}]")
        return
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(image_path, width=width)
    cap = doc.add_paragraph()
    cap_run = cap.add_run(caption)
    set_run_font(cap_run, italic=True)
    cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(12)


def build_content(doc: Document) -> None:
    add_index_page(doc)

    add_heading(doc, "Introducción")
    add_body(
        doc,
        "El presente informe documenta el diseño e implementación de IntegraBot, copiloto "
        "de Recursos Humanos para IntegraServicios S.A., desarrollado como respuesta a la "
        "Evaluación Parcial N°1 de la asignatura Ingeniería de Soluciones con IA (ISY0101). "
        "El objetivo del informe es describir el caso organizacional, la ingeniería de prompts, "
        "el pipeline RAG con corpus dual (interno y externo), la arquitectura modular de la "
        "solución y las evidencias de prueba, justificando cada decisión técnica según los "
        "requerimientos del encargo.",
    )
    add_body(
        doc,
        "IntegraBot utiliza Retrieval-Augmented Generation (RAG) con LangChain, ChromaDB, "
        "embeddings gemini-embedding-001 y el modelo gemini-3.6-flash, expuesto mediante "
        "Streamlit. El repositorio del proyecto está disponible en "
        "https://github.com/DeboradorDeMundos/integraservicios-rrhh.",
    )

    add_heading(doc, "1. Análisis del caso organizacional (IE1)")
    add_body(
        doc,
        "IntegraServicios S.A. es una empresa de servicios cuya área de Gestión de Personas "
        "recibe aproximadamente 750 tickets mensuales sobre beneficios, permisos, reglamento "
        "interno y normativa laboral chilena, incluida la Ley Karin (N° 21.643). Gran parte "
        "de estas consultas son repetitivas, generan demoras y exponen a la organización al "
        "riesgo de respuestas informales o desactualizadas con consecuencias legales.",
    )
    add_table(
        doc,
        "Tabla 1. Objetivos de intervención de IntegraBot",
        ["Objetivo", "Meta"],
        [
            ["Autogestión de consultas frecuentes", "Disponibilidad 24/7"],
            ["Tiempo de respuesta", "Menor a 5 segundos"],
            ["Precisión normativa", "0 % invención; derivación explícita sin evidencia"],
        ],
    )
    add_heading(doc, "1.1 Datos disponibles y restricciones", level=2)
    add_table(
        doc,
        "Tabla 2. Corpus dual indexado",
        ["Tipo", "Documento", "Contenido clave"],
        [
            ["Interno", "RIOHS_IntegraServicios_2026.pdf", "Jornada, licencias, EPP, Ley Karin"],
            ["Interno", "Contrato_Colectivo_2026.pdf", "Colación, días admin., aguinaldo, escolaridad"],
            ["Externo", "Codigo_del_Trabajo_Chile.pdf", "Horas extra, finiquitos, Ley Karin"],
        ],
    )
    add_body(
        doc,
        "Los PDF se generan con generate_data.py para reproducibilidad evaluativa; el pipeline "
        "equivale al de documentos oficiales en producción. IntegraBot no reemplaza asesoría "
        "legal ni investigaciones Ley Karin, no incluye autenticación ni portal RRHH real, y "
        "escala casos sensibles (sumarios, finiquitos litigiosos) a Gestión de Personas.",
    )
    add_body(
        doc,
        "Se descartó fine-tuning por la mutabilidad del corpus, chatbots genéricos por "
        "alucinación de montos y agentes autónomos abiertos por falta de trazabilidad. RAG "
        "permite recuperar evidencia, generar con contexto acotado, actualizar documentos sin "
        "reentrenar y citar la fuente en cada respuesta.",
    )

    add_heading(doc, "2. Formulación de prompts (IE2)")
    add_body(
        doc,
        "IntegraBot actúa como Copiloto de RRHH y Cumplimiento Laboral. El System Prompt "
        "(src/prompts.py) establece reglas de obligado cumplimiento: responder únicamente con "
        "el contexto recuperado; nunca inventar plazos, bonos ni artículos; citar siempre con "
        "el formato [Fuente: archivo.pdf, Art./Cláusula]; y usar la frase institucional exacta "
        "de derivación cuando no exista evidencia documental.",
    )
    add_body(
        doc,
        "El prompt recibe inyección triple: {context} (fragmentos MMR), {question} y "
        "{chat_history} (últimas tres interacciones). La temperature se fija en 0,1 para "
        "respuestas deterministas en temas legales. Como segunda capa, guardrails.py valida "
        "post-generación: si la respuesta está vacía o carece de cita y derivación, fuerza la "
        "frase: «No dispongo de la información oficial en los manuales de la empresa ni en el "
        "Código del Trabajo para responder con certeza. He derivado tu consulta al equipo de "
        "Gestión de Personas».",
    )

    add_heading(doc, "3. Pipeline RAG dual (IE3)")
    add_body(
        doc,
        "El flujo implementado es: consulta del colaborador en Streamlit → historial acotado "
        "(conversation.py) → retriever MMR con k=4 sobre ChromaDB → contexto formateado con "
        "metadata source_type → System Prompt + Gemini → guardrails → respuesta con expander "
        "de fuentes documentales.",
    )
    add_table(
        doc,
        "Tabla 3. Parámetros técnicos del pipeline RAG",
        ["Componente", "Implementación", "Justificación"],
        [
            ["Carga", "PyPDFDirectoryLoader", "Extracción de PDF corporativos"],
            ["Fragmentación", "Chunk 500 / overlap 50", "Respeta artículos y cláusulas"],
            ["Embeddings", "gemini-embedding-001", "Búsqueda semántica"],
            ["Vector store", "ChromaDB ./chroma_db_v2", "Persistencia local, baja latencia"],
            ["Retriever", "MMR k=4, λ=0,75", "Relevancia con diversidad de fuentes"],
            ["LLM", "gemini-3.6-flash", "Generación documental eficiente"],
        ],
    )
    add_body(
        doc,
        "Ejemplos verificables del corpus: bono de colación $85.000 (Contrato Colectivo), "
        "3 días administrativos pagados, aguinaldo Fiestas Patrias $180.000, denuncia Ley Karin "
        "vía denuncias@integraservicios.cl (RIOHS), y horas extraordinarias con recargo del "
        "50 % según Art. 32 del Código del Trabajo.",
    )

    add_heading(doc, "4. Arquitectura de la solución (IE4)")
    add_body(
        doc,
        "La solución se estructura en ocho módulos desacoplados bajo src/ más app.py. "
        "config.py centraliza el caso organizacional y parámetros RAG; ingestion.py gestiona "
        "carga, etiquetado interno/externo e indexación; prompts.py y guardrails.py implementan "
        "IE2; conversation.py limita el historial a tres turnos; rag_engine.py orquesta el "
        "RAGPipeline; errors.py traduce fallos técnicos a mensajes institucionales; y app.py "
        "entrega la interfaz conversacional con trazabilidad RAG visible.",
    )
    add_body(
        doc,
        "La Figura 1 representa el flujo arquitectónico completo: el colaborador interactúa "
        "vía Streamlit (app.py); el historial acotado pasa por conversation.py; rag_engine.py "
        "orquesta la recuperación MMR desde ChromaDB; el contexto alimenta prompts.py y "
        "Gemini; guardrails.py valida la respuesta; y la UI muestra el expander de fuentes "
        "documentales con trazabilidad interno/externo.",
    )
    add_figure(
        doc,
        DIAGRAM_PATH,
        "Figura 1. Arquitectura RAG de IntegraBot (corpus dual, MMR k=4, Gemini y guardrails).",
    )

    add_heading(doc, "5. Pruebas, limitaciones y repositorio (IE5)")
    add_body(
        doc,
        "Se implementó scripts/smoke_test.py con validación offline (corpus, metadata "
        "source_type, guardrails, historial) y modo --live con seis consultas de demostración, "
        "incluyendo pregunta fuera de dominio («¿Mañana va a llover?») que debe derivar sin "
        "inventar. Limitaciones declaradas: PDF simulados, dependencia de cuota Google AI "
        "Studio, ausencia de login e integración productiva con portal RRHH.",
    )
    add_table(
        doc,
        "Tabla 4. Casos de prueba representativos",
        ["Consulta", "Resultado esperado"],
        [
            ["Bono de colación", "$85.000 + cita Contrato Colectivo"],
            ["Días administrativos", "3 días + cita"],
            ["Ley Karin", "Procedimiento + cita RIOHS/Código"],
            ["Horas extraordinarias", "Art. 32 + recargo 50 %"],
            ["¿Mañana va a llover?", "Derivación institucional"],
        ],
    )

    add_heading(doc, "Conclusión")
    add_body(
        doc,
        "Tras el análisis e implementación, se deduce que IntegraBot responde de forma "
        "pertinente al caso organizacional de IntegraServicios S.A.: reduce carga en "
        "consultas repetitivas, mantiene trazabilidad mediante citas explícitas y escala a "
        "Gestión de Personas cuando no hay evidencia documental. La arquitectura modular y el "
        "corpus dual interno/externo evidencian los indicadores IE1 a IE4; las pruebas "
        "automatizadas y el repositorio GitHub respaldan la reproducibilidad exigida en IE5.",
    )
    add_heading(doc, "Reflexión individual", level=2)
    add_body(
        doc,
        "Diego Alejandro Madrid Muñoz: Durante este encargo comprendí en la práctica cómo "
        "un pipeline RAG no es solo conectar un LLM a un chat, sino diseñar recuperación, "
        "prompts y guardrails como capas complementarias. Implementé y integré la arquitectura "
        "modular (config, ingestion, prompts, guardrails, conversation, rag_engine y app.py), "
        "el corpus dual con metadata source_type y las pruebas smoke_test.py. La mayor "
        "dificultad fue gestionar cuotas de la API de Gemini y asegurar que el modelo no "
        "inventara montos en consultas laborales; lo resolví bajando la temperature, "
        "forzando citas en el prompt y validando respuestas en guardrails.py. Mi aporte "
        "consistió en dejar un sistema ejecutable, documentado y alineado a la rúbrica, "
        "priorizando trazabilidad sobre apariencia de chatbot genérico.",
    )
    add_heading(doc, "Declaración de uso de inteligencia artificial", level=2)
    add_body(
        doc,
        "Se empleó IA generativa (Cursor IDE, Google Gemini API) como apoyo en revisión de "
        "código, borrador de documentación y diagramas. El análisis del caso, las decisiones "
        "de diseño, las conclusiones y la reflexión individual son responsabilidad del "
        "autor. Referencia institucional: Duoc UC (2025), "
        "https://bibliotecas.duoc.cl/ia.",
    )

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


def main() -> None:
    source = TEMPLATE_PATH if os.path.isfile(TEMPLATE_PATH) else DOC_PATH
    if not os.path.isfile(source):
        print(f"No encontrado: {source}", file=sys.stderr)
        raise SystemExit(1)

    doc = Document(source)
    update_cover(doc)
    finalize_cover_page_break(doc)
    clear_body_after_cover(doc)
    build_content(doc)
    try:
        doc.save(DOC_PATH)
        print(f"Informe regenerado: {DOC_PATH} (desde {os.path.basename(source)})")
    except PermissionError:
        alt = os.path.join(ROOT, "Informe EP1 ISY0101_corregido.docx")
        doc.save(alt)
        print(
            f"Cierra Word y vuelve a ejecutar el script.\n"
            f"Copia guardada en: {alt}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
