#!/usr/bin/env python
"""Genera presentacion_ep2.html con slides completas y guion para video (~10 min)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "presentacion_ep2.html"

# Slides: html + time + note (guion oral detallado)
SLIDES = [
    {
        "html": """
          <div class="logo rise">IB</div>
          <div class="kicker rise">Evaluación Parcial N°2 · ISY0101 · Duoc UC</div>
          <h1 class="rise">IntegraBot Agente</h1>
          <p class="lead rise">Evolución del copiloto RAG (EP1) a un <strong>agente funcional</strong> con herramientas de consulta y escritura, memoria de caso, planificación y orquestación LangChain — mismo caso IntegraServicios S.A.</p>
          <div class="rise" style="margin-top:14px">
            <span class="chip">Diego Alejandro Madrid Muñoz</span>
            <span class="chip">IntegraServicios · Gestión de Personas</span>
            <span class="chip">LangChain Tools · Chroma · Gemini</span>
          </div>
        """,
        "time": "0:00 – 0:45",
        "note": (
            "Buenos días. Soy Diego Madrid. En la Evaluación Parcial 2 presento IntegraBot ya no "
            "como un pipeline RAG fijo, sino como agente organizacional: integra consulta documental, "
            "escritura de tickets RRHH, memoria de caso y decisiones adaptativas. Es la continuación "
            "directa del EP1, con el mismo corpus dual y los mismos guardrails anti-alucinación."
        ),
    },
    {
        "html": """
          <div class="kicker">Mapa de la exposición</div>
          <h2 class="rise">Qué voy a mostrar (10 minutos)</h2>
          <div class="row">
            <div class="card"><h3>1. EP1 → EP2</h3><p>Por qué evolucionar a agente</p></div>
            <div class="card"><h3>2. Tools + framework</h3><p>LangChain ReAct · bind_tools</p></div>
            <div class="card"><h3>3. Memoria + RAG</h3><p>Corto/largo plazo · Chroma MMR</p></div>
          </div>
          <div class="row">
            <div class="card"><h3>4. Planificación</h3><p>Clasificación adaptativa · planner</p></div>
            <div class="card"><h3>5. Orquestación</h3><p>Módulos · flujo · justificación</p></div>
            <div class="card"><h3>6. Demo + pruebas</h3><p>Streamlit · scripts · video en vivo</p></div>
          </div>
        """,
        "time": "0:45 – 1:15",
        "note": (
            "Les dejo el mapa: primero el salto conceptual de EP1 a EP2; luego las cuatro herramientas "
            "y el framework; memoria dual y recuperación semántica; planificador de tareas; arquitectura "
            "y justificación técnica; cierro con demo en Streamlit y scripts de prueba reproducibles."
        ),
    },
    {
        "html": """
          <div class="kicker">Continuidad del proyecto</div>
          <h2 class="rise">EP1 entregó RAG · EP2 exige agente</h2>
          <div class="row-2">
            <div class="card"><span class="ie">EP1</span><h3>Copiloto RAG</h3><ul><li>Retrieve → Gemini → guardrails</li><li>Corpus interno + externo</li><li>Citas obligatorias</li></ul></div>
            <div class="card"><span class="ie green">EP2</span><h3>Agente funcional</h3><ul><li>Tools: consulta + escritura</li><li>Memoria de caso + tickets INT</li><li>Planner + decisiones</li></ul></div>
          </div>
          <p class="sub">No descartamos el RAG: lo encapsulamos dentro de herramientas especializadas.</p>
        """,
        "time": "1:15 – 2:00",
        "note": (
            "La rúbrica EP2 pide agente con consulta, escritura y razonamiento. EP1 ya resolvía consulta "
            "con evidencia. EP2 agrega autonomía controlada: el sistema elige cuándo buscar interno, "
            "externo, guardar memoria o abrir ticket. El RAG no se tira: vive en buscar_politicas_internas "
            "y buscar_normativa_externa, reutilizando Chroma, MMR y guardrails."
        ),
    },
    {
        "html": """
          <div class="kicker">Caso organizacional</div>
          <h2 class="rise">IntegraServicios · ~750 tickets/mes</h2>
          <div class="row">
            <div class="card"><p>Meta</p><div class="metric"><em data-count="750">0</em></div><p>consultas/mes a RRHH</p></div>
            <div class="card"><p>Agente resuelve</p><div class="metric">FAQ</div><p>24/7 con trazabilidad</p></div>
            <div class="card"><p>Escala</p><div class="metric">INT</div><p>Tickets + humanos en sensibles</p></div>
          </div>
        """,
        "time": "2:00 – 2:35",
        "note": (
            "Mantengo el caso de EP1: Gestión de Personas saturada con consultas repetitivas. "
            "El agente automatiza FAQs documentadas; en finiquitos litigiosos, sumarios o acoso "
            "orienta con normativa pero escala con ticket INT y límites claros — no reemplaza "
            "investigación Ley Karin ni asesoría legal."
        ),
    },
    {
        "html": """
          <div class="kicker">Por qué agente</div>
          <h2 class="rise">Tres capacidades en un flujo</h2>
          <table>
            <tr><th>Tipo</th><th>Tool</th><th>Por qué</th></tr>
            <tr><td>Consulta</td><td>buscar_politicas_internas</td><td>RIOHS + Contrato antes de responder montos</td></tr>
            <tr><td>Consulta</td><td>buscar_normativa_externa</td><td>Código / Ley Karin sin mezclar corpus</td></tr>
            <tr><td>Escritura</td><td>guardar_memoria_caso</td><td>Continuidad en conversaciones largas</td></tr>
            <tr><td>Escritura</td><td>registrar_ticket_gestion_personas</td><td>Trazabilidad RRHH (INT-xxxxx)</td></tr>
          </table>
        """,
        "time": "2:35 – 3:20",
        "note": (
            "Cuatro herramientas autónomas: consulta y escritura. Separé dos retrievers porque en RRHH mezclar reglamento "
            "interno con Código del Trabajo sin etiqueta es riesgo. Escritura: memoria JSON por sesión "
            "y tickets mock locales — reproducible para el evaluador, equivalente a integrar tiquetera "
            "en producción."
        ),
    },
    {
        "html": """
          <div class="kicker">Framework</div>
          <h2 class="rise">LangChain Agents (ReAct)</h2>
          <div class="flow">
            <div class="pill sm">System + plan</div><div class="arrow">→</div>
            <div class="pill sm">bind_tools</div><div class="arrow">→</div>
            <div class="pill sm">tool_calls</div><div class="arrow">→</div>
            <div class="pill sm">ToolMessage</div><div class="arrow">→</div>
            <div class="pill sm">respuesta</div>
          </div>
          <p class="sub">Implementación: <span class="mono">src/agent.py</span> · hasta 4 turnos · Gemini <span class="mono">gemini-3.6-flash</span></p>
        """,
        "time": "3:20 – 4:00",
        "note": (
            "Framework de agentes: LangChain con bind_tools y bucle ReAct — el mismo patrón "
            "que LangChain Agents documenta. El planner inyecta el plan al system prompt; el LLM "
            "decide qué tool invocar. Escalabilidad: RAGPipeline desacoplado; compatibilidad: "
            "MODEL_PROVIDER local ejecuta el plan de forma determinista si no hay API."
        ),
    },
    {
        "html": """
          <div class="kicker">Memoria</div>
          <h2 class="rise">Corto plazo + largo plazo</h2>
          <div class="row-2">
            <div class="card"><h3>Corto</h3><p><span class="mono">conversation.py</span></p><p>Últimos 8 turnos en prompt — follow-ups inmediatos</p></div>
            <div class="card"><h3>Largo</h3><p><span class="mono">memory.py</span></p><p><span class="mono">case_memory/{session}.json</span> — hechos, tema, tickets</p></div>
          </div>
          <p class="quote">Ejemplo: «¿y el ticket que abrimos?» recupera memoria de caso + nueva búsqueda.</p>
        """,
        "time": "4:00 – 4:45",
        "note": (
            "Memoria de contenido en flujos prolongados. Corto plazo: ventana de mensajes. "
            "Largo plazo: cada sesión Streamlit tiene session_id; guardamos hechos y IDs de ticket. "
            "Así el agente no trata cada mensaje como aislado — requisito clave de EP2 frente a EP1."
        ),
    },
    {
        "html": """
          <div class="kicker">Recuperación semántica</div>
          <h2 class="rise">Chroma MMR con filtro de corpus</h2>
          <div class="row">
            <div class="card"><span class="chip tag-in">interno</span><h3>filter source_type</h3><p>RIOHS · Contrato</p></div>
            <div class="card"><span class="chip tag-ex">externo</span><h3>filter source_type</h3><p>Código del Trabajo</p></div>
            <div class="card"><h3>MMR k=4</h3><p>Relevancia + diversidad</p></div>
          </div>
          <p class="sub"><span class="mono">retriever.py</span> comparte índice EP1 · <span class="mono">chroma_db_v2</span></p>
        """,
        "time": "4:45 – 5:20",
        "note": (
            "Recuperación semántica para continuidad. Reutilizo embeddings gemini-embedding-001 "
            "y Chroma de EP1, pero EP2 expone dos retrievers filtrados. El agente puede buscar solo "
            "interno para beneficios, o externo si detecta Ley Karin o horas extra — alineado al flujo."
        ),
    },
    {
        "html": """
          <div class="kicker">Planificación</div>
          <h2 class="rise">planner.py — prioridades explícitas</h2>
          <div class="row-4">
            <div class="card"><h3>FAQ</h3><p>1 búsqueda + cita</p></div>
            <div class="card"><h3>Multietapa</h3><p>Interno + externo + memoria</p></div>
            <div class="card"><h3>Sensible</h3><p>Ticket INT + límites</p></div>
            <div class="card"><h3>Fuera dominio</h3><p>Derivación sin RAG</p></div>
          </div>
          <p class="sub">UI: expander «Orquestación del agente (EP2)» — evidencia para el evaluador.</p>
        """,
        "time": "5:20 – 6:00",
        "note": (
            "Antes de actuar, classify_task define el tipo de consulta y build_execution_plan "
            "genera pasos numerados con prioridad alta/media. Eso es planificación visible, no caja negra. "
            "En sensible detectamos palabras como finiquito o sumario; en clima no consultamos corpus — "
            "decisión adaptativa al entorno."
        ),
    },
    {
        "html": """
          <div class="kicker">Orquestación</div>
          <h2 class="rise">Módulos y flujo de datos</h2>
          <div class="mod-grid rise">
            <div class="mod"><strong>app.py</strong>UI · trazas EP2</div>
            <div class="mod"><strong>agent.py</strong>run_agent · ReAct</div>
            <div class="mod"><strong>planner.py</strong>clasificar · plan</div>
            <div class="mod"><strong>agent_tools.py</strong>4 tools</div>
            <div class="mod"><strong>memory.py</strong>caso · sesión</div>
            <div class="mod"><strong>retriever.py</strong>corpus · MMR</div>
            <div class="mod"><strong>rag_engine.py</strong>síntesis + guardrails</div>
            <div class="mod"><strong>tickets.py</strong>INT-xxxxx</div>
          </div>
          <div class="flow">
            <div class="pill sm">Usuario</div><div class="arrow">→</div>
            <div class="pill sm">Plan</div><div class="arrow">→</div>
            <div class="pill sm">Tools</div><div class="arrow">→</div>
            <div class="pill sm">RAG</div><div class="arrow">→</div>
            <div class="pill sm">Respuesta</div>
          </div>
        """,
        "time": "6:00 – 6:45",
        "note": (
            "Orquestación: app.py llama run_agent; planner clasifica; tools ejecutan consulta o "
            "escritura; rag_engine y guardrails de EP1 validan la respuesta final. Diagrama en informe "
            "y docs/diagrama_orquestacion_ep2.png. README documenta pasos para evaluador externo."
        ),
    },
    {
        "html": """
          <div class="kicker">Guardrails EP1 preservados</div>
          <h2 class="rise">Cero invención · citas · derivación</h2>
          <div class="row-2">
            <div class="card"><h3>prompts.py + guardrails.py</h3><ul><li>Temperature 0.1</li><li>Frase institucional exacta</li><li>[Fuente: pdf, Art.]</li></ul></div>
            <div class="card"><h3>Agente no es abogado</h3><ul><li>Orienta con documentos</li><li>Ticket en escalamiento</li><li>Humano en sumarios</li></ul></div>
          </div>
        """,
        "time": "6:45 – 7:15",
        "note": (
            "Decisione de diseño EP2: no relajar EP1 por tener agente. El LLM con tools sigue "
            "obligado a citar; guardrails fuerzan derivación si no hay evidencia. El agente amplía "
            "capacidades, no permisos para inventar montos o plazos."
        ),
    },
    {
        "html": """
          <div class="kicker">Justificación técnica</div>
          <h2 class="rise">Por qué cada componente</h2>
          <table>
            <tr><th>Elección</th><th>Alineación al flujo RRHH</th></tr>
            <tr><td>ReAct vs cadena fija EP1</td><td>EP2 exige autonomía con tools</td></tr>
            <tr><td>Dos retrievers</td><td>Separar política interna y ley externa</td></tr>
            <tr><td>Memoria JSON</td><td>Flujos multietapa sin inflar tokens</td></tr>
            <tr><td>Tickets mock</td><td>Escritura auditable en evaluación</td></tr>
            <tr><td>Streamlit</td><td>Demo oral con trazas visibles</td></tr>
          </table>
        """,
        "time": "7:15 – 7:50",
        "note": (
            "Cada pieza responde un requerimiento organizacional del caso. "
            "No usé AutoGen porque el caso necesita trazabilidad documental estilo EP1; LangChain "
            "integra RAG + tools en un solo stack ya probado en el proyecto."
        ),
    },
    {
        "html": """
          <div class="kicker">Pruebas</div>
          <h2 class="rise">Evidencia reproducible</h2>
          <table>
            <tr><th>Script</th><th>Qué valida</th></tr>
            <tr><td>agent_scenarios_test.py</td><td>Planner, memoria, FAQ, sensible, fuera dominio</td></tr>
            <tr><td>smoke_test.py --live</td><td>Regresión corpus RAG EP1</td></tr>
          </table>
          <p class="sub">GitHub: README · diagrama · instrucciones de ejecución</p>
        """,
        "time": "7:50 – 8:15",
        "note": (
            "Encargo pide evidencia de pruebas. agent_scenarios_test prueba planificación y ticket "
            "en caso sensible offline; con --live valida tools con Gemini. Capturas de salida y de "
            "Streamlit van al informe y AVA."
        ),
    },
    {
        "html": """
          <div class="kicker">Demo en vivo</div>
          <h2 class="rise">localhost:8501 — guión de grabación</h2>
          <div class="row" style="grid-template-columns:1fr">
            <div class="card"><p><span class="demo-num">1</span><strong>Colación</strong> → plan FAQ · tools · cita Contrato · expander fuentes</p></div>
            <div class="card"><p><span class="demo-num">2</span><strong>Días admin + documentos</strong> → multietapa · memoria · dos búsquedas</p></div>
            <div class="card"><p><span class="demo-num">3</span><strong>¿Mañana llover?</strong> → fuera dominio · derivación · sin inventar</p></div>
            <div class="card"><p><span class="demo-num">4</span><strong>Sumario / finiquito litigioso</strong> → sensible · ticket INT · orquestación</p></div>
            <div class="card"><p><span class="demo-num">5</span><strong>Follow-up</strong> «¿estado del ticket?» → memoria larga de caso</p></div>
          </div>
        """,
        "time": "8:15 – 11:30",
        "note": (
            "BLOQUE DEMO PARA VIDEO. Tener Streamlit con MODEL_PROVIDER=google. En cada pregunta: "
            "1) Leer plan en Orquestación. 2) Mencionar tools usadas. 3) Abrir fuentes RAG. "
            "4) En sensible mostrar INT-xxxxx. Frase clave: el agente decide el flujo según "
            "el tipo de consulta. Si la API falla, mostrar expander con plan local."
        ),
    },
    {
        "html": """
          <div class="kicker">Limitaciones honestas</div>
          <h2 class="rise">Alcance declarado</h2>
          <div class="row-2">
            <div class="card"><ul><li>PDF simulados (pipeline real)</li><li>Tickets mock INT</li><li>Sin login / portal RRHH</li></ul></div>
            <div class="card"><ul><li>Dependencia API Gemini</li><li>No investigación Ley Karin</li><li>Declaración IA Duoc en informe</li></ul></div>
          </div>
        """,
        "time": "11:30 – 11:50",
        "note": (
            "Igual que EP1: honestidad sobre límites. El agente escala lo sensible; no sustituye "
            "sumarios ni asesoría legal. Reflexión individual y conclusiones en informe son propias, "
            "sin IA, según pauta Duoc."
        ),
    },
    {
        "html": """
          <div class="kicker">Cierre</div>
          <h2 class="rise">Planifica · recuerda · consulta · escribe · deriva</h2>
          <p class="lead">IntegraBot EP2 demuestra un agente organizacional controlado sobre el mismo corpus RRHH, con trazabilidad EP1 y autonomía exigida en EP2.</p>
          <p class="sub" style="margin-top:16px">Diego Madrid · ISY0101 · Repositorio GitHub · Gracias</p>
        """,
        "time": "11:50 – 12:00",
        "note": (
            "Cierre: EP2 cumple herramientas, memoria, planificación y orquestación documentadas. "
            "Invito preguntas sobre ReAct, memoria de caso o planner. Para el video: terminar "
            "con agradecimiento y enlace al repo si la plataforma lo permite."
        ),
    },
]

VIEWS = [
    {"name": "INICIO", "x": 0, "y": 18, "z": 40, "ry": 0.04, "rx": 0.22, "rz": 0, "zoom": 0.72, "vx": "50%", "vy": "46%", "pulse": 1.0},
    {"name": "MAPA", "x": 80, "y": -20, "z": -10, "ry": 0.55, "rx": 0.15, "rz": 0.03, "zoom": 1.0, "vx": "58%", "vy": "42%", "pulse": 1.05},
    {"name": "EP1EP2", "x": -60, "y": 30, "z": 20, "ry": -0.4, "rx": 0.1, "rz": 0, "zoom": 1.15, "vx": "42%", "vy": "50%", "pulse": 1.1},
    {"name": "CASO", "x": 40, "y": 8, "z": -25, "ry": 0.35, "rx": 0.12, "rz": 0.05, "zoom": 1.2, "vx": "48%", "vy": "44%", "pulse": 1.15},
    {"name": "TOOLS", "x": 20, "y": -12, "z": 10, "ry": 0.2, "rx": 0.18, "rz": 0, "zoom": 1.3, "vx": "52%", "vy": "40%", "pulse": 1.18},
    {"name": "FRAME", "x": 55, "y": -18, "z": -20, "ry": 0.48, "rx": 0.2, "rz": 0, "zoom": 1.35, "vx": "54%", "vy": "42%", "pulse": 1.2},
    {"name": "MEMC", "x": -70, "y": 25, "z": 30, "ry": -0.5, "rx": 0.16, "rz": 0, "zoom": 1.4, "vx": "38%", "vy": "50%", "pulse": 1.22},
    {"name": "SEM", "x": 30, "y": 10, "z": 15, "ry": 0.28, "rx": 0.1, "rz": 0.03, "zoom": 1.45, "vx": "50%", "vy": "46%", "pulse": 1.25},
    {"name": "PLAN", "x": 10, "y": 5, "z": 0, "ry": 0.12, "rx": 0.06, "rz": 0, "zoom": 1.5, "vx": "50%", "vy": "48%", "pulse": 1.28},
    {"name": "ORQ", "x": 8, "y": 4, "z": 8, "ry": 0.15, "rx": 0.05, "rz": 0, "zoom": 1.55, "vx": "50%", "vy": "48%", "pulse": 1.3},
    {"name": "GUARD", "x": -20, "y": -8, "z": -30, "ry": -0.15, "rx": 0.22, "rz": 0, "zoom": 1.5, "vx": "46%", "vy": "44%", "pulse": 1.25},
    {"name": "JUST", "x": 90, "y": 30, "z": 50, "ry": 0.7, "rx": 0.12, "rz": 0.05, "zoom": 1.15, "vx": "62%", "vy": "48%", "pulse": 1.08},
    {"name": "TEST", "x": -100, "y": 15, "z": 35, "ry": -0.65, "rx": 0.08, "rz": -0.04, "zoom": 1.1, "vx": "36%", "vy": "48%", "pulse": 1.05},
    {"name": "DEMO", "x": 0, "y": 0, "z": 0, "ry": 0.08, "rx": 0.04, "rz": 0, "zoom": 2.0, "vx": "50%", "vy": "48%", "pulse": 1.55},
    {"name": "LIMIT", "x": -120, "y": 40, "z": 60, "ry": -0.9, "rx": 0.25, "rz": 0.08, "zoom": 0.95, "vx": "32%", "vy": "55%", "pulse": 0.92},
    {"name": "CIERRE", "x": 0, "y": 25, "z": 75, "ry": 0.1, "rx": 0.28, "rz": 0, "zoom": 0.65, "vx": "50%", "vy": "38%", "pulse": 0.85},
]


def js_string(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def build_slides_js() -> str:
    parts = ["const slides = ["]
    for slide in SLIDES:
        parts.append("      {")
        parts.append(f"        html: `{slide['html'].strip()}`, ")
        parts.append(f"        time: {js_string(slide['time'])}, ")
        parts.append(f"        note: {js_string(slide['note'])}")
        parts.append("      },")
    parts.append("    ];")
    return "\n".join(parts)


def build_views_js() -> str:
    lines = ["      const views = ["]
    for v in VIEWS:
        lines.append(
            "        { "
            f"name: {js_string(v['name'])}, x: {v['x']}, y: {v['y']}, z: {v['z']}, "
            f"ry: {v['ry']}, rx: {v['rx']}, rz: {v['rz']}, zoom: {v['zoom']}, "
            f"vx: {js_string(v['vx'])}, vy: {js_string(v['vy'])}, pulse: {v['pulse']} "
            "},"
        )
    lines.append("      ];")
    return "\n".join(lines)


def main() -> None:
    import sys

    text = HTML.read_text(encoding="utf-8")
    if "--sync-slides" in sys.argv:
        start = text.index("const slides = [")
        end = text.index('document.getElementById("tot")')
        slides_block = build_slides_js() + "\n\n    "
        text = text[:start] + slides_block + text[end:]
    else:
        print("Slides: sin cambios (edita presentacion_ep2.html). Usa --sync-slides para volcar SLIDES[].")

    vstart = text.index("const views = [")
    vend = text.index("let cam = { ...views[0] };")
    text = text[:vstart] + build_views_js() + "\n      " + text[vend:]

    text = text.replace(
        'SLIDE <span id="sl">01</span>/<span id="tot">10</span>',
        f'SLIDE <span id="sl">01</span>/<span id="tot">{len(SLIDES):02d}</span>',
    )
    hint = '<div class="hint">← → avanzar · <b>N</b> notas / guion · <b>F</b> pantalla completa</div>'
    text = text.replace(
        '<div class="hint">← → · <b>F</b> pantalla completa</div>',
        hint,
    )
    HTML.write_text(text, encoding="utf-8")
    print(f"OK {HTML.name}: {len(SLIDES)} slides, guion en notas (tecla `)")


if __name__ == "__main__":
    main()
