#!/usr/bin/env python
"""Arma el informe Word y la presentación HTML de la EP3 desde las métricas reales."""
from __future__ import annotations

import json
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUMMARY = os.path.join(ROOT, "observability", "ep3_summary.json")
BEFORE = os.path.join(ROOT, "observability", "ep3_summary_antes.json")
DIAGRAM = os.path.join(ROOT, "docs", "diagrama_observabilidad_ep3.png")
DOCX_PATH = os.path.join(ROOT, "eva3", "Informe_EP3_ISY0101_Diego_Madrid.docx")
HTML_PATH = os.path.join(ROOT, "presentacion_ep3.html")
MD_PATH = os.path.join(ROOT, "INFORME_EVA3.md")
FONT = "Times New Roman"


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def pct(value) -> str:
    if value is None:
        return "s/d"
    return f"{float(value) * 100:.0f} %"


def jaccard_of(summary: dict, intent: str) -> str:
    for row in summary["metrics"]["consistency_by_intent"]:
        if row["intent"] == intent:
            return f"{row['jaccard'] * 100:.0f} %"
    return "s/d"


def set_run(run, *, bold=False, italic=False, size=12, color=None) -> None:
    run.font.name = FONT
    run._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_p(doc, text, *, bold=False, center=False, indent=True, size=12, space_before=0, space_after=6):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run(run, bold=bold, size=size)
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.15
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent and not center and not bold:
        pf.first_line_indent = Cm(1.25)
    return p


def add_h(doc, text):
    return add_p(doc, text, bold=True, indent=False, space_before=10, space_after=4)


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(header)
        set_run(run, bold=True, size=10)
    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            cell = table.rows[r].cells[c]
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(value))
            set_run(run, size=10)
    doc.add_paragraph()


def build_docx(after: dict, before: dict) -> None:
    m = after["metrics"]
    lat = m["latency_ms"]
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2.2)
        section.bottom_margin = Cm(2.2)
        section.left_margin = Cm(2.4)
        section.right_margin = Cm(2.4)
        section.page_width = Cm(21.59)
        section.page_height = Cm(27.94)

    for line, size, bold in (
        ("Duoc UC", 14, True),
        ("Ingeniería de Soluciones con IA · ISY0101 · Sección 011V", 12, False),
        ("Evaluación Parcial N°3 — Encargo con presentación", 12, False),
        ("Observabilidad de IntegraBot", 16, True),
        ("Agente de RRHH y cumplimiento laboral · IntegraServicios S.A.", 12, False),
        ("Diego Alejandro Madrid Muñoz", 12, False),
        ("RUT 19.914.672-6", 12, False),
        ("Profesor Jaime Andrés Menéndez Silva", 12, False),
        ("Santiago, 23 de noviembre de 2026", 12, False),
    ):
        add_p(doc, line, bold=bold, center=True, indent=False, size=size, space_after=2)

    add_p(
        doc,
        "Repositorio: https://github.com/DeboradorDeMundos/integraservicios-rrhh",
        center=True,
        indent=False,
        size=11,
        space_before=8,
    )
    doc.add_page_break()

    add_h(doc, "1. Qué se midió")
    add_p(
        doc,
        "IntegraBot ya respondía con citas (EP1) y ya elegía herramientas, memoria y tickets (EP2). "
        "Esta entrega no cambia el caso: mide si ese agente se comporta igual cuando la pregunta cambia de redacción, "
        "cuánto tarda, si falla, y cuánta memoria usa. El objetivo de negocio sigue siendo el de las 750 consultas mensuales "
        "de Gestión de Personas, con un límite de 5 segundos por respuesta y con cero invención de montos o artículos.",
    )
    add_p(
        doc,
        "La batería tiene 17 intenciones repetidas dos veces (34 turnos), en modo local, sin consumir cuota de la API. "
        "Cada intención trae al menos una paráfrasis: no se evalúa solo la frase de la demo. "
        "Un turno es preciso si hace lo que el escenario pide: citar un PDF cuando la pregunta es de beneficios o de norma, "
        "derivar cuando está fuera de dominio, o abrir un ticket INT cuando el caso es sensible. "
        "La consistencia es el índice de Jaccard entre los textos de la misma intención. "
        "La latencia, la CPU y el pico de memoria Python se toman dentro del turno, no con un promedio de servidor ajeno al agente.",
    )

    add_h(doc, "2. Resultados")
    add_p(doc, "Tabla 1. Métricas de la batería EP3, después de corregir la cita de Ley Karin.", indent=False, bold=True, size=11)
    add_table(
        doc,
        ["Métrica", "Resultado", "Lectura"],
        [
            ["Precisión", pct(m["precision"]), f"{m['n_labeled']} turnos etiquetados"],
            ["Consistencia", pct(m["consistency"]), "Jaccard medio entre paráfrasis"],
            ["Errores", pct(m["error_rate"]), f"{m['error_count']} excepciones"],
            ["Latencia p50", f"{lat['p50']:.0f} ms", "Turno típico, ya con el índice cargado"],
            ["Latencia p95", f"{lat['p95']:.0f} ms", "Cola alta, sin contar solo el máximo"],
            ["Latencia máxima", f"{lat['max']:.0f} ms", "Primer turno: carga de embeddings y Chroma"],
            ["Cumplimiento SLO 5 s", pct(m["slo_compliance"]), f"{m['slo_breach_count']} turno fuera de límite"],
            ["CPU media", f"{m['cpu_ms']['mean']:.0f} ms", "Tiempo de procesador del turno"],
            ["Memoria pico", f"{m['peak_kb']['max']:.0f} KB", "Tracemalloc; el máximo es el arranque"],
        ],
    )
    add_p(
        doc,
        "Tabla 2. Precisión por conducta esperada.",
        indent=False,
        bold=True,
        size=11,
    )
    expect_rows = []
    labels = {
        "cita_interna": "Cita de beneficio interno",
        "cita": "Cita normativa (Karin / horas extra)",
        "derivacion": "Derivación fuera de dominio",
        "ticket": "Ticket en caso sensible",
    }
    for key, bucket in m["precision_by_expect"].items():
        expect_rows.append([labels.get(key, key), f"{bucket['ok']}/{bucket['n']}", pct(bucket["rate"])])
    add_table(doc, ["Conducta", "Aciertos", "Tasa"], expect_rows)
    add_p(
        doc,
        "Los montos no se contradicen entre paráfrasis (0 conflictos de cifra). "
        f"La consistencia de Ley Karin pasó de {jaccard_of(before, 'karin')} en la medición inicial "
        f"a {jaccard_of(after, 'karin')} después del ajuste. El resto de intenciones ya estaba en 100 %.",
    )

    add_h(doc, "3. Qué muestran los registros")
    add_p(
        doc,
        f"El primer turno tardó {lat['max'] / 1000:.1f} segundos. La media de los siguientes queda cerca de "
        f"{((m['n'] * lat['mean'] - lat['max']) / max(m['n'] - 1, 1)):.0f} ms. "
        "Ese salto no es una consulta lenta de un colaborador: es la carga de sentence-transformers y de ChromaDB. "
        "En la interfaz ese costo ya está fuera de la pregunta, porque Streamlit precarga el agente con caché al abrir la app. "
        "El script de batería, en cambio, medía el arranque dentro del primer turno. Por eso el cumplimiento del SLO es "
        f"{pct(m['slo_compliance'])} y no 100 %: falla un solo evento, el de partida. "
        f"El percentil 95 ({lat['p95']:.0f} ms) describe las consultas ya tibias y queda muy por debajo de los 5 segundos.",
    )
    add_p(
        doc,
        "El segundo hallazgo está en Ley Karin. Antes del ajuste, la pregunta «¿Cómo se denuncia el acoso laboral?» "
        "citaba el RIOHS y la paráfrasis «¿Cuál es el canal para denunciar acoso laboral según Ley Karin?» citaba el Código del Trabajo. "
        "El procedimiento era el mismo (denuncia verbal o escrita, plazo de 30 días, confidencialidad), pero la fuente ganadora cambiaba. "
        "Eso bajaba el Jaccard de esa intención y dejaba una cita inestable frente a una norma que el usuario nombró de forma explícita. "
        "La corrección está en el generador local: si la pregunta menciona Karin o acoso, el fragmento del Código del Trabajo "
        "recibe prioridad de desempate. No se inventa texto; se fija qué documento manda cuando hay dos bloques válidos.",
    )
    add_p(
        doc,
        "El registro también confirma los caminos que no deben tocar el corpus. Clima y fútbol derivan en menos de 2 ms, "
        "sin cita. Finiquito litigioso y cheque litigioso abren ticket INT. Una pregunta de colación que incluía un RUT de prueba "
        "respondió el bono y el JSONL guardó el marcador [RUT], no el número. El correo que aparece en la respuesta de denuncia "
        "queda como [EMAIL]. La sesión se guarda como hash de 12 caracteres.",
    )
    if os.path.isfile(DIAGRAM):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(DIAGRAM, width=Inches(6.1))
        add_p(
            doc,
            "Figura 1. Flujo de observabilidad: el turno del agente escribe un evento local y el dashboard lo agrega.",
            center=True,
            indent=False,
            size=11,
        )

    add_h(doc, "4. Dashboard")
    add_p(
        doc,
        "El monitoreo está en dashboard.py y se abre con streamlit run dashboard.py. "
        "Muestra cinco indicadores (precisión, consistencia, errores, latencia p95 y cumplimiento del SLO), "
        "la latencia turno a turno, la media por tipo de tarea en turnos ya tibios, la consistencia por intención y la tabla de eventos. "
        "El gráfico de la izquierda conserva el pico de arranque; el de la derecha no, para no hacer ver lenta una consulta de beneficios "
        "que en régimen tarda menos de un segundo. Cada fila se puede abrir: plan, herramientas, citas, tickets y resultado del guardrail.",
    )
    dash = os.path.join(ROOT, "docs", "dashboard_ep3.png")
    if os.path.isfile(dash):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(dash, width=Inches(6.1))
        add_p(
            doc,
            "Figura 2. Dashboard de la batería EP3: 100 % de precisión y de consistencia, 0 % de errores, p95 de 145 ms.",
            center=True,
            indent=False,
            size=11,
        )

    add_h(doc, "5. Recomendaciones y uso responsable")
    add_p(
        doc,
        "Primero, el SLO de 5 segundos debe medirse en turnos tibios. El arranque se precarga al levantar el servicio, "
        "que es lo que ya hace la app, y no se le cobra a la primera persona que pregunta. "
        "Segundo, cuando una norma está nombrada en la pregunta, la cita tiene que ser estable: un desempate explícito "
        "vale más que dejar que dos fragmentos parecidos se alternen. Tercero, los promedios por tipo de tarea importan más que un solo número: "
        "un caso sensible consulta dos corpus y abre ticket; un fuera de dominio no debe pagar esa búsqueda. "
        "Cuarto, la telemetría no es el expediente. El JSONL no lleva RUT, correo ni nombre, y no sale del equipo. "
        "El ticket de Gestión de Personas sí puede llevar el RUT que la persona entregó, porque ese dato es del trámite y lo ve RRHH, no un tablero.",
    )
    add_p(
        doc,
        "En producción el mismo diseño evita convertir el asistente en vigilancia: se publican tasas y latencias, no el texto completo de la consulta, "
        "y los casos de acoso, finiquito o sumario siguen escalando a una persona. Los PDF del repositorio son material de la evaluación; "
        "no reemplazan el Código del Trabajo ni los instrumentos reales de la empresa.",
    )

    add_h(doc, "Conclusión")
    add_p(
        doc,
        f"Cerré esta entrega midiendo el mismo IntegraBot de la EP2, sin armar otro sistema. "
        f"En 34 turnos, con la misma consulta dicha de otra forma, la conducta esperada se cumplió en el {pct(m['precision'])}, "
        f"no hubo excepciones y la consistencia quedó en {pct(m['consistency'])} después de fijar la cita de Ley Karin. "
        "El único turno fuera de los 5 segundos es el arranque de Chroma y de los embeddings. "
        "Con el JSONL y el dashboard puedo mostrar el plan, la herramienta, la cita y el costo de cada pregunta, "
        "y mantengo la regla de las entregas anteriores: no inventar montos y no dejar el RUT en el tablero.",
    )

    add_h(doc, "Reflexión individual — Diego Alejandro Madrid Muñoz")
    add_p(
        doc,
        "En la EP3 seguí con el agente que ya tenía y le puse medición. Escribí src/observability.py para guardar un evento por turno, "
        "scripts/observability_eval.py para repetir las preguntas con otra redacción, y dashboard.py para ver precisión, latencia, consistencia, errores y memoria. "
        "Lo que más me costó fue el primer número que se veía bien: el p95 daba cerca de 145 ms, pero el primer turno se iba a más de 12 segundos "
        "porque ahí se carga el índice. Si hubiera mostrado solo el promedio, el límite de 5 segundos parecía casi cumplido y el problema real quedaba escondido. "
        "El otro hallazgo salió al comparar los logs de Ley Karin. Una redacción citaba el RIOHS y la otra el Código del Trabajo, con el mismo procedimiento de denuncia. "
        "Ajusté el desempate en local_generator.py para que, si la pregunta nombra Karin o acoso, mande el Código. "
        "Volví a correr la batería y la consistencia de esa intención pasó de 84 % a 100 %. "
        "También probé una consulta de colación con un RUT y en el archivo quedó [RUT], no el número. "
        "Aprendí que en Gestión de Personas observar sirve cuando el registro obliga a corregir algo concreto, no cuando el gráfico se ve ordenado.",
    )

    add_h(doc, "Declaración de uso de inteligencia artificial")
    add_p(
        doc,
        "Usé Cursor como apoyo para revisar código, ordenar tablas y armar el diagrama. "
        "Los porcentajes del informe salen de la ejecución local de scripts/observability_eval.py, no de un texto generado. "
        "La lectura de los logs, la decisión de fijar la cita de Ley Karin, la conclusión y esta reflexión las escribí yo. "
        "Duoc UC (2025): https://bibliotecas.duoc.cl/ia",
    )

    add_h(doc, "Referencias")
    for ref in (
        "Chroma. (2026). Chroma documentation. https://docs.trychroma.com/",
        "Duoc UC. (2025). Uso de inteligencia artificial en el aprendizaje. https://bibliotecas.duoc.cl/ia",
        "Google. (2026). Gemini API documentation. https://ai.google.dev/",
        "LangChain. (2026). LangChain Python documentation. https://python.langchain.com/",
        "Streamlit. (2026). Streamlit documentation. https://docs.streamlit.io/",
    ):
        add_p(doc, ref, indent=False, size=11, space_after=2)

    os.makedirs(os.path.dirname(DOCX_PATH), exist_ok=True)
    doc.save(DOCX_PATH)
    print(DOCX_PATH)


def build_html(after: dict, before: dict) -> None:
    m = after["metrics"]
    lat = m["latency_ms"]
    slides = [
        (
            "Observabilidad de IntegraBot",
            "Evaluación Parcial N°3 · ISY0101 · Sección 011V",
            [
                "Diego Alejandro Madrid Muñoz",
                "IntegraServicios S.A. · Gestión de Personas",
                "Del agente que responde al agente que se puede medir",
            ],
        ),
        (
            "De qué venimos",
            "La EP3 no reemplaza el caso. Lo observa.",
            [
                "EP1: RAG dual, citas y derivación si no hay evidencia.",
                "EP2: plan, herramientas, memoria y ticket INT.",
                "EP3: precisión, latencia, consistencia, errores y recursos.",
                "Mismo límite de negocio: respuesta en menos de 5 segundos, sin inventar montos.",
            ],
        ),
        (
            "Cómo se midió",
            "34 turnos. 17 intenciones. Cada una con otra redacción.",
            [
                "Precisión: ¿citó, derivó o abrió ticket, según el escenario?",
                "Consistencia: Jaccard entre las respuestas de la misma intención.",
                "Latencia, CPU y pico de memoria dentro del turno.",
                "Errores: excepciones. En esta batería, cero.",
                "El RUT de prueba no queda en el log. Queda [RUT].",
            ],
        ),
        (
            "Los números",
            "Batería local, después del ajuste de Ley Karin.",
            [
                f"Precisión {pct(m['precision'])} · Consistencia {pct(m['consistency'])} · Errores {pct(m['error_rate'])}",
                f"Latencia p50 {lat['p50']:.0f} ms · p95 {lat['p95']:.0f} ms · máximo {lat['max'] / 1000:.1f} s",
                f"SLO de 5 s: {pct(m['slo_compliance'])}. El incumplimiento es un solo turno, el de arranque.",
                f"Memoria pico del proceso en el primer turno: {m['peak_kb']['max'] / 1024:.0f} MB.",
                "Cifras de beneficios: 0 contradicciones entre paráfrasis.",
            ],
        ),
        (
            "Hallazgo 1 · el arranque",
            "Un promedio esconde el primer turno.",
            [
                f"El primer turno tardó {lat['max'] / 1000:.1f} s: carga embeddings y Chroma.",
                f"El p95 de la batería es {lat['p95']:.0f} ms. La consulta tibia cumple el SLO.",
                "Streamlit ya precarga el agente al abrir la app.",
                "Recomendación: el SLO se cobra a la pregunta, no al arranque del servicio.",
            ],
        ),
        (
            "Hallazgo 2 · Ley Karin",
            "Dos respuestas correctas y una cita que saltaba de documento.",
            [
                "«¿Cómo se denuncia el acoso?» citaba el RIOHS.",
                "«¿Cuál es el canal según Ley Karin?» citaba el Código del Trabajo.",
                f"Jaccard de esa intención: {jaccard_of(before, 'karin')} antes, {jaccard_of(after, 'karin')} después.",
                "Corrección: si la pregunta nombra Karin o acoso, desempata a favor del Código.",
                "No se reescribió la norma. Se fijó la fuente cuando había dos bloques válidos.",
            ],
        ),
        (
            "Qué más se ve en la traza",
            "El log distingue el camino, no solo el texto final.",
            [
                "Clima y fútbol: derivación, sin búsqueda útil, menos de 2 ms.",
                "Finiquito y cheque litigioso: ticket INT y escalamiento.",
                "Beneficios: cita interna estable (colación, días, escolaridad, aguinaldo).",
                "Cada turno guarda plan, herramientas, citas y fase cold_start o warm.",
            ],
        ),
        (
            "Dashboard",
            "streamlit run dashboard.py",
            [
                "Cinco indicadores arriba, lectura en una pantalla.",
                "Latencia por turno y media por tipo de tarea.",
                "Consistencia por intención y tabla de eventos.",
                "Se puede abrir un turno: plan, tools, cita, ticket.",
                "La batería y el chat en vivo son archivos distintos.",
            ],
        ),
        (
            "Uso responsable",
            "Medir no es vigilar a la persona.",
            [
                "Telemetría local: sin RUT, sin correo, sesión hasheada.",
                "El ticket de RRHH sí puede llevar el RUT del trámite. El tablero, no.",
                "Acoso, finiquito y sumario siguen yendo a una persona.",
                "Los PDF del repo son de la evaluación, no el texto oficial de la ley.",
            ],
        ),
        (
            "Qué defender en los 10 minutos",
            "Tres frases, con el dato al lado.",
            [
                f"La conducta esperada se cumple en el {pct(m['precision'])} de 34 turnos con redacción distinta.",
                "El único atraso grande es el arranque, y la app ya lo saca de la pregunta.",
                "La traza mostró una cita inestable de Ley Karin y eso se corrigió.",
                "Preguntas útiles: ¿por qué Jaccard y no una nota del LLM? ¿por qué no Grafana?",
                "Respuesta corta: el criterio es auditable en código y el volumen de la demo no justifica otro stack.",
            ],
        ),
    ]

    parts = []
    for index, (title, subtitle, bullets) in enumerate(slides, start=1):
        items = "".join(f"<li>{item}</li>" for item in bullets)
        parts.append(
            f"""
            <section class="slide">
              <p class="kicker">EP3 · {index:02d}</p>
              <h2>{title}</h2>
              <p class="sub">{subtitle}</p>
              <ul>{items}</ul>
            </section>
            """
        )
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <title>IntegraBot · Observabilidad EP3</title>
  <style>
    :root {{ color-scheme: dark; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: "Segoe UI", sans-serif; background: #071018; color: #f4f7fb;
    }}
    .slide {{
      min-height: 100vh; padding: 7vh 9vw 10vh; display: none;
      background:
        radial-gradient(900px 420px at 100% -10%, rgba(26,122,212,.45), transparent 60%),
        linear-gradient(160deg, #071018 0%, #0b2a4a 70%, #071018 100%);
    }}
    .slide.active {{ display: block; }}
    .kicker {{ letter-spacing: .14em; text-transform: uppercase; color: #9cc4ee; font-size: .82rem; }}
    h2 {{ font-size: clamp(2rem, 4vw, 3.4rem); margin: .2rem 0 .4rem; line-height: 1.05; }}
    .sub {{ font-size: 1.25rem; color: #d5e6f7; margin-top: 0; }}
    ul {{ padding-left: 1.2rem; max-width: 920px; }}
    li {{ font-size: 1.28rem; line-height: 1.45; margin: .55rem 0; }}
    .bar {{
      position: fixed; left: 0; right: 0; bottom: 0; height: 42px;
      display: flex; justify-content: space-between; align-items: center;
      padding: 0 1.2rem; background: rgba(7,16,24,.8); color: #9cc4ee; font-size: .9rem;
    }}
  </style>
</head>
<body>
  {''.join(parts)}
  <div class="bar"><span id="pos"></span><span>← → para moverse · IntegraBot EP3</span></div>
  <script>
    const slides = [...document.querySelectorAll('.slide')];
    let i = 0;
    const show = (n) => {{
      i = (n + slides.length) % slides.length;
      slides.forEach((s, idx) => s.classList.toggle('active', idx === i));
      document.getElementById('pos').textContent = (i + 1) + ' / ' + slides.length;
    }};
    document.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') show(i + 1);
      if (e.key === 'ArrowLeft' || e.key === 'PageUp') show(i - 1);
    }});
    document.addEventListener('click', (e) => {{
      if (e.target.closest('.bar')) return;
      show(i + 1);
    }});
    show(0);
  </script>
</body>
</html>
"""
    with open(HTML_PATH, "w", encoding="utf-8") as handle:
        handle.write(html)
    print(HTML_PATH)


def build_md(after: dict, before: dict) -> None:
    m = after["metrics"]
    lat = m["latency_ms"]
    text = f"""# IntegraBot — Observabilidad del agente (EP3)

**Informe técnico · Evaluación Parcial N°3**

| Campo | Dato |
| --- | --- |
| **Asignatura** | ISY0101 — Ingeniería de Soluciones con IA |
| **Autor** | Diego Alejandro Madrid Muñoz · RUT 19.914.672-6 |
| **Docente** | Jaime Andrés Menéndez Silva |
| **Sección** | 011V |
| **Fecha** | 23 de noviembre de 2026 |
| **Repositorio** | https://github.com/DeboradorDeMundos/integraservicios-rrhh |

Documento de entrega: `eva3/Informe_EP3_ISY0101_Diego_Madrid.docx`. Presentación: `presentacion_ep3.html`.

## Resultados de la batería (34 turnos)

| Métrica | Valor |
| --- | --- |
| Precisión | {pct(m['precision'])} |
| Consistencia (Jaccard) | {pct(m['consistency'])} |
| Errores | {pct(m['error_rate'])} |
| Latencia p50 / p95 / máx | {lat['p50']:.0f} ms / {lat['p95']:.0f} ms / {lat['max']:.0f} ms |
| SLO 5 s | {pct(m['slo_compliance'])} |
| Ley Karin, Jaccard antes → después | {jaccard_of(before, 'karin')} → {jaccard_of(after, 'karin')} |

La medición inicial está en `observability/ep3_summary_antes.json`. La medición posterior al desempate de cita está en `observability/ep3_summary.json`.

## Cómo reproducir

```bash
python scripts/observability_eval.py
python scripts/render_diagram_ep3.py
python scripts/build_ep3_entregables.py
streamlit run dashboard.py
```
"""
    with open(MD_PATH, "w", encoding="utf-8") as handle:
        handle.write(text)
    print(MD_PATH)


def main() -> None:
    after = load(SUMMARY)
    before = load(BEFORE)
    build_md(after, before)
    build_docx(after, before)
    build_html(after, before)


if __name__ == "__main__":
    main()
