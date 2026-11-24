#!/usr/bin/env python
"""Arma presentacion_ep3.html con el mismo deck visual y el guion de la EP2."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "presentacion_ep2.html"
OUT = ROOT / "presentacion_ep3.html"

SLIDES = [
    {
        "html": """
          <div class="logo rise">IB</div>
          <div class="kicker rise">Evaluación Parcial N°3 · ISY0101 · Duoc UC</div>
          <h1 class="rise">IntegraBot Observabilidad</h1>
          <p class="lead rise">El mismo agente de la EP2, ahora <strong>medido</strong>: precisión, latencia, consistencia, errores y recursos, con registro local y dashboard. Caso IntegraServicios S.A.</p>
          <div class="hero-stats rise">
            <div class="hero-stat"><b>100%</b><span>Precisión</span></div>
            <div class="hero-stat"><b>145 ms</b><span>Latencia p95</span></div>
            <div class="hero-stat"><b>0%</b><span>Errores</span></div>
            <div class="hero-stat"><b>5 s</b><span>SLO de respuesta</span></div>
          </div>
          <div class="rise tag-row">
            <span class="chip">Diego Alejandro Madrid Muñoz</span>
            <span class="chip">IntegraServicios · Gestión de Personas</span>
            <span class="chip">JSONL · Streamlit · Chroma</span>
          </div>
        """,
        "time": "0:00 – 0:40",
        "note": (
            "Hola, soy Diego Madrid. IntegraBot es el asistente de Gestión de Personas de IntegraServicios. "
            "Un colaborador pregunta por un bono, un permiso o una norma, y el sistema responde solo con lo que está escrito "
            "en el reglamento interno, el contrato colectivo o el Código del Trabajo. Si el dato no está, no lo inventa: lo deriva a una persona. "
            "En la primera entrega eso era una búsqueda con citas. En la segunda ya podía ordenar los pasos, recordar la conversación y abrir un ticket. "
            "Hoy lo que hago es medirlo: ver si acierta, cuánto se demora y si se mantiene cuando la misma pregunta se dice de otra forma."
        ),
    },
    {
        "html": """
          <div class="slide-head"><div class="kicker">Mapa de la exposición</div><h2 class="rise">Qué voy a mostrar (10 minutos)</h2></div>
          <div class="row">
            <div class="card accent-gold"><span class="step-badge">01</span><div class="card-icon">📏</div><h3>Métricas</h3><p>Precisión, latencia, consistencia, errores, RAM</p></div>
            <div class="card accent-cyan"><span class="step-badge">02</span><div class="card-icon">📜</div><h3>Registros</h3><p>Arranque en frío y cita de Ley Karin</p></div>
            <div class="card accent-violet"><span class="step-badge">03</span><div class="card-icon">📊</div><h3>Dashboard</h3><p>Batería EP3 + chat en vivo</p></div>
          </div>
          <div class="row">
            <div class="card accent-green"><span class="step-badge">04</span><div class="card-icon">🛡️</div><h3>Uso responsable</h3><p>Sin RUT ni correo en la telemetría</p></div>
            <div class="card accent-blue"><span class="step-badge">05</span><div class="card-icon">🎬</div><h3>Demo</h3><p>Chat 8501 y dashboard 8502</p></div>
            <div class="card accent-orange"><span class="step-badge">06</span><div class="card-icon">🔧</div><h3>Mejora</h3><p>SLO tibio y desempate de cita</p></div>
          </div>
        """,
        "time": "0:40 – 1:10",
        "note": (
            "Les cuento el recorrido para que sepan dónde estamos. Parto por qué medí y con qué números quedé. "
            "Después les muestro dos cosas que aparecieron al mirar los registros, no en el promedio. "
            "Sigo con el tablero, con el cuidado de los datos personales, y termino escribiendo en el chat para que vean el mismo turno aparecer en el dashboard."
        ),
    },
    {
        "html": """
          <div class="slide-head"><div class="kicker">Continuidad del proyecto</div><h2 class="rise">EP1 citó · EP2 actuó · EP3 mide</h2></div>
          <div class="row">
            <div class="card accent-cyan"><span class="ie">EP1</span><h3>Copiloto RAG</h3><ul><li>Citas obligatorias</li><li>Derivación sin inventar</li><li>Corpus dual</li></ul></div>
            <div class="card accent-violet"><span class="ie">EP2</span><h3>Agente</h3><ul><li>Plan y herramientas</li><li>Memoria y ticket INT</li><li>Mismos guardrails</li></ul></div>
            <div class="card accent-gold"><span class="ie gold">EP3</span><h3>Observabilidad</h3><ul><li>JSONL por turno</li><li>Métricas y dashboard</li><li>Corrección con evidencia</li></ul></div>
          </div>
        """,
        "time": "1:10 – 1:45",
        "note": (
            "Esto es la misma línea de trabajo, no un proyecto nuevo. Primero el sistema aprendió a contestar citando el documento. "
            "Después aprendió a decidir: buscar en el reglamento, buscar en la ley, guardar el caso o abrir un ticket. "
            "Ahora cada una de esas respuestas queda anotada. Cuánto tardó, qué herramienta usó y si citó, derivó o escaló. El tablero solo lee esas anotaciones."
        ),
    },
    {
        "html": """
          <div class="slide-head"><div class="kicker">Qué se midió</div><h2 class="rise">Cinco señales sobre el mismo agente</h2></div>
          <div class="tbl-glass rise">
          <table>
            <tr><th>Métrica</th><th>Cómo se decide</th><th>Indicador</th></tr>
            <tr><td>Precisión</td><td>Cita, deriva o abre ticket según el caso</td><td><span class="ie">IE1</span></td></tr>
            <tr><td>Consistencia</td><td>Jaccard entre paráfrasis de la misma intención</td><td><span class="ie">IE1</span></td></tr>
            <tr><td>Errores</td><td>Excepciones por turno</td><td><span class="ie">IE1</span></td></tr>
            <tr><td>Latencia</td><td>P50, P95 y SLO de 5 segundos</td><td><span class="ie green">IE2</span></td></tr>
            <tr><td>Recursos</td><td>CPU del turno y pico de memoria Python</td><td><span class="ie green">IE2</span></td></tr>
          </table>
          </div>
        """,
        "time": "1:45 – 2:30",
        "note": (
            "No me quedé con la pregunta bonita de la demo. Armé 17 temas y cada uno lo pregunté de dos maneras, dos veces. Son 34 turnos. "
            "Cuando digo precisión me refiero a algo concreto: si era un beneficio, tenía que citar; si era el clima, tenía que derivar; si era un finiquito, tenía que abrir ticket. "
            "Consistencia es que las dos formas de preguntar lo mismo no terminen diciendo montos distintos. "
            "Latencia es el tiempo de la respuesta, con un tope de 5 segundos que viene del caso. Y recursos es la CPU y la memoria de ese turno, no un promedio del computador entero."
        ),
    },
    {
        "html": """
          <div class="slide-head"><div class="kicker">Resultados</div><h2 class="rise">34 turnos · modo local</h2></div>
          <div class="row-4">
            <div class="card accent-green"><p>Precisión</p><div class="metric"><em>100%</em></div><p>34 / 34</p></div>
            <div class="card accent-cyan"><p>Consistencia</p><div class="metric"><em>100%</em></div><p>después del ajuste</p></div>
            <div class="card accent-gold"><p>Errores</p><div class="metric"><em>0%</em></div><p>sin excepciones</p></div>
            <div class="card accent-blue"><p>p95</p><div class="metric"><em>145</em></div><p>milisegundos</p></div>
          </div>
          <p class="sub">SLO de 5 s: <strong>97 %</strong>. El único turno fuera de límite es el arranque, 12,6 s. P50: 71 ms.</p>
        """,
        "time": "2:30 – 3:15",
        "note": (
            "Corrí la batería en local, sin gastar la cuota de la API, y estos son los números que salieron. "
            "Las 34 respuestas hicieron lo que correspondía. Ninguna se cayó por un error. "
            "Las consultas ya con el sistema cargado andan en torno a 70 milisegundos, y casi todas quedan bajo 145. "
            "El 97 por ciento cumple los 5 segundos. El 3 por ciento que falta es un solo turno, el primero, y de ese hablo ahora."
        ),
    },
    {
        "html": """
          <div class="slide-head"><div class="kicker">Hallazgo 1 · registros</div><h2 class="rise">El promedio escondía el arranque</h2></div>
          <div class="row-2">
            <div class="card accent-orange"><div class="card-icon">❄️</div><h3>Primer turno</h3><p class="metric" style="font-size:42px"><em>12,6 s</em></p><p>Carga de embeddings y Chroma</p></div>
            <div class="card accent-green"><div class="card-icon">⚡</div><h3>Turnos siguientes</h3><p class="metric" style="font-size:42px"><em>72 ms</em></p><p>Dentro del SLO de 5 segundos</p></div>
          </div>
          <p class="quote rise">En el chat, Streamlit ya precarga el agente. El SLO se cobra a la pregunta, no al arranque del servicio.</p>
        """,
        "time": "3:15 – 4:10",
        "note": (
            "Si yo les mostrara solo el promedio, parecería que todo está holgado. El percentil 95 da 145 milisegundos y uno dice listo, cumple. "
            "Pero el primer turno se fue a 12 segundos y medio. Ahí no está pensando la respuesta: está cargando el modelo de embeddings y la base Chroma. "
            "Las que vienen después bajan a unos 70 milisegundos. Por eso en el chat ese costo queda al abrir la aplicación, no se lo cobro a la persona que pregunta."
        ),
    },
    {
        "html": """
          <div class="slide-head"><div class="kicker">Hallazgo 2 · registros</div><h2 class="rise">Ley Karin citaba dos PDF distintos</h2></div>
          <div class="row-2">
            <div class="card accent-orange"><span class="ie gold">Antes</span><h3>Jaccard 84 %</h3><ul><li>«¿Cómo se denuncia el acoso?» → RIOHS</li><li>«¿Cuál es el canal según Ley Karin?» → Código</li><li>Mismo procedimiento, fuente inestable</li></ul></div>
            <div class="card accent-green"><span class="ie green">Después</span><h3>Jaccard 100 %</h3><ul><li>Si la pregunta nombra Karin o acoso</li><li>Desempata el Código del Trabajo</li><li>No se reescribe la norma</li></ul></div>
          </div>
        """,
        "time": "4:10 – 5:00",
        "note": (
            "Este hallazgo me gustó más, porque las dos respuestas estaban bien en el fondo. "
            "Las dos decían que la denuncia puede ser verbal o escrita, que la investigación no pasa de 30 días y que se cuida la confidencialidad. "
            "El problema era la fuente: una redacción citaba el reglamento de la empresa y la otra el Código del Trabajo. "
            "Para quien lee, parece que la norma cambia según cómo preguntes. "
            "Dejé un desempate simple: si la persona nombra Ley Karin o acoso, manda el Código. Volví a correr la prueba y las cuatro quedaron citando el mismo PDF."
        ),
    },
    {
        "html": """
          <div class="slide-head"><div class="kicker">Trazabilidad</div><h2 class="rise">Cada turno deja un evento</h2></div>
          <div class="flow">
            <div class="pill sm">Chat</div><div class="arrow">→</div>
            <div class="pill sm">run_agent</div><div class="arrow">→</div>
            <div class="pill sm">JSONL</div><div class="arrow">→</div>
            <div class="pill sm">Métricas</div><div class="arrow">→</div>
            <div class="pill sm">dashboard.py</div>
          </div>
          <div class="row" style="margin-top:16px">
            <div class="card accent-cyan"><h3>FAQ</h3><p>Cita interna · colación, días, escolaridad</p></div>
            <div class="card accent-violet"><h3>Fuera de dominio</h3><p>Clima y fútbol · derivación · sin cita</p></div>
            <div class="card accent-orange"><h3>Sensible</h3><p>Finiquito o cheque · ticket INT</p></div>
          </div>
        """,
        "time": "5:00 – 5:40",
        "note": (
            "Cada mensaje del chat deja una fila. No guardo solo la respuesta final. Queda el plan, qué herramienta se usó y de qué PDF salió el dato. "
            "Si preguntan si mañana llueve, el sistema deriva al tiro y no se pone a buscar el clima en el contrato. "
            "Si alguien llega con un finiquito litigioso, abre un ticket y lo escala. "
            "Y metí a propósito un RUT en una pregunta de colación: en el archivo no aparece el número, aparece la marca RUT."
        ),
    },
    {
        "html": """
          <div class="slide-head"><div class="kicker">El tablero</div><h2 class="rise">Aquí se ven las 34 pruebas</h2></div>
          <div class="row">
            <div class="card accent-cyan"><div class="card-icon">1️⃣</div><h3>Arriba, cinco números</h3><p>Precisión, consistencia, errores, tiempo y si cumple los 5 segundos.</p></div>
            <div class="card accent-orange"><div class="card-icon">2️⃣</div><h3>La línea del tiempo</h3><p>El primer punto es el arranque. Los demás son la consulta normal.</p></div>
            <div class="card accent-gold"><div class="card-icon">3️⃣</div><h3>En la demo</h3><p>Marco Chat en vivo, aprieto Actualizar y aparece la pregunta que acabo de escribir.</p></div>
          </div>
        """,
        "time": "5:40 – 6:20",
        "note": (
            "Esta lámina es el tablero, todavía no el chat. Tiene tres partes, de izquierda a derecha. "
            "La primera: arriba están los cinco números, precisión, consistencia, errores, tiempo y si cumple los 5 segundos. "
            "La segunda: la línea del tiempo. El primer punto, el que se dispara, es el arranque. Los que quedan abajo son la consulta normal. "
            "La tercera la uso en la demo: marco Chat en vivo, aprieto Actualizar, y la pregunta que escriba en el chat aparece en la tabla."
        ),
    },
    {
        "html": """
          <div class="slide-head"><div class="kicker">Los datos de la persona</div><h2 class="rise">El tablero no guarda el RUT</h2></div>
          <div class="row-2">
            <div class="card accent-green"><div class="card-icon">📊</div><h3>Esto sí queda en el tablero</h3><ul><li>Si la respuesta acertó</li><li>Cuánto demoró</li><li>Qué herramienta usó</li></ul></div>
            <div class="card accent-orange"><div class="card-icon">🙈</div><h3>Esto no queda</h3><ul><li>Ni el RUT ni el correo ni el nombre</li><li>Si alguien lo escribe, el registro dice solo «RUT»</li><li>El ticket lo ve una persona de RRHH, no el gráfico</li></ul></div>
          </div>
        """,
        "time": "6:20 – 7:00",
        "note": (
            "Esta lámina son dos tarjetas. La verde es lo que sí guarda el tablero: si acertó, cuánto demoró y qué herramienta usó. "
            "La naranja es lo que no guarda: ni RUT, ni correo, ni nombre. "
            "Lo probé. Escribí un RUT dentro de una pregunta de colación y en el archivo no salió el número: salió la palabra RUT. "
            "El ticket es otra cosa. Ese lo abre Recursos Humanos y lo ve una persona, no este gráfico."
        ),
    },
    {
        "html": """
          <div class="slide-head"><div class="kicker">Mejoras con los datos</div><h2 class="rise">Qué cambié después de medir</h2></div>
          <div class="tbl-glass rise">
          <table>
            <tr><th>Decisión</th><th>Evidencia</th></tr>
            <tr><td>SLO solo en turnos tibios</td><td>Máximo 12,6 s · media siguiente 72 ms</td></tr>
            <tr><td>Desempate Ley Karin</td><td>Jaccard 84 % → 100 %</td></tr>
            <tr><td>Media por tipo de tarea</td><td>Sensible abre ticket; clima no busca</td></tr>
            <tr><td>Registro sin datos personales</td><td>Prueba de RUT quedó como [RUT]</td></tr>
          </table>
          </div>
        """,
        "time": "7:00 – 7:40",
        "note": (
            "Estas no son ideas sueltas. Cada fila salió de algo que vi en los registros. "
            "El límite de 5 segundos lo mido cuando el sistema ya está despierto, porque el arranque es otra cosa. "
            "La cita de Karin la fijé porque saltaba de documento. "
            "Y separé el tablero del expediente para poder mirar el desempeño sin llevarme los datos de la persona."
        ),
    },
    {
        "html": """
          <div class="slide-head"><div class="kicker">Demo en vivo</div><h2 class="rise">Chat <span class="mono">8501</span> · dashboard <span class="mono">8502</span></h2></div>
          <div class="row" style="grid-template-columns:1fr">
            <div class="card accent-cyan"><p><span class="demo-num">1</span><strong>Bono de colación</strong> · cita del contrato · latencia baja</p></div>
            <div class="card accent-violet"><p><span class="demo-num">2</span><strong>¿Mañana va a llover?</strong> · derivación · sin inventar</p></div>
            <div class="card accent-orange"><p><span class="demo-num">3</span><strong>Finiquito litigioso</strong> · ticket INT · escalamiento</p></div>
            <div class="card accent-green"><p><span class="demo-num">4</span>Dashboard · <strong>Chat en vivo</strong> · <strong>Actualizar</strong> · abrir el turno</p></div>
          </div>
        """,
        "time": "7:40 – 10:30",
        "note": (
            "Ahora lo hago en vivo. Dejo esta lámina y me paso al chat. "
            "Primero pregunto el bono de colación. Si se demora, digo que es la carga del índice y no la respuesta. "
            "Después pregunto si mañana va a llover, para que se vea que deriva y no inventa el clima. "
            "Y después un finiquito litigioso, para que abra el ticket. "
            "Vuelvo al dashboard, marco Chat en vivo, actualizo y abro una de esas filas: ahí está el plan, la herramienta y cómo terminó."
        ),
    },
    {
        "html": """
          <div class="slide-head"><div class="kicker">Cierre</div><h2 class="rise">El agente queda observable</h2></div>
          <p class="lead rise">Mismo corpus, mismos guardrails, y ahora cada respuesta tiene medida, fuente y límite.</p>
          <div class="pillar-row rise">
            <span class="pillar"><i>📏</i> Mide</span>
            <span class="pillar"><i>📜</i> Registra</span>
            <span class="pillar"><i>📊</i> Muestra</span>
            <span class="pillar"><i>🔧</i> Corrige</span>
            <span class="pillar"><i>🔒</i> Protege</span>
          </div>
          <p class="sub" style="margin-top:clamp(16px,3vh,28px);text-align:center">Diego Madrid · ISY0101 · GitHub · Gracias</p>
        """,
        "time": "10:30 – 11:00",
        "note": (
            "Para cerrar. IntegraBot sigue siendo el asistente de personas que contesta con documentos y deriva lo que no sabe. "
            "En esta entrega le puse una forma de mirarlo. En 34 preguntas distintas acertó lo que tenía que hacer, no se cayó, "
            "y el único atraso grande fue prender el índice. Mirando los registros pillé una cita de Ley Karin que cambiaba de PDF, y eso quedó corregido. "
            "Gracias, quedo atento a las preguntas."
        ),
    },
]

VIEWS = [
    ("INICIO", 0, 18, 40, 0.04, 0.22, 0, 0.72, "50%", "46%", 1.0),
    ("MAPA", 80, -20, -10, 0.55, 0.15, 0.03, 1.0, "58%", "42%", 1.05),
    ("EP123", -60, 30, 20, -0.4, 0.1, 0, 1.15, "42%", "50%", 1.1),
    ("METRICAS", 40, 8, -25, 0.35, 0.12, 0.05, 1.2, "48%", "44%", 1.15),
    ("NUMEROS", 20, -12, 10, 0.2, 0.18, 0, 1.3, "52%", "40%", 1.18),
    ("ARRANQUE", 55, -18, -20, 0.48, 0.2, 0, 1.35, "54%", "42%", 1.2),
    ("KARIN", -70, 25, 30, -0.5, 0.16, 0, 1.4, "38%", "50%", 1.22),
    ("TRAZA", 30, 10, 15, 0.28, 0.1, 0.03, 1.45, "50%", "46%", 1.25),
    ("DASH", 10, 5, 0, 0.12, 0.06, 0, 1.5, "50%", "48%", 1.28),
    ("ETICA", 8, 4, 8, 0.15, 0.05, 0, 1.55, "50%", "48%", 1.3),
    ("MEJORA", -20, -8, -30, -0.15, 0.22, 0, 1.5, "46%", "44%", 1.25),
    ("DEMO", 0, 0, 0, 0.08, 0.04, 0, 2.0, "50%", "48%", 1.55),
    ("CIERRE", 0, 25, 75, 0.1, 0.28, 0, 0.65, "50%", "38%", 0.85),
]


def _views_js() -> str:
    rows = []
    for name, x, y, z, ry, rx, rz, zoom, vx, vy, pulse in VIEWS:
        rows.append(
            "        { name: "
            + json.dumps(name)
            + f", x: {x}, y: {y}, z: {z}, ry: {ry}, rx: {rx}, rz: {rz}, zoom: {zoom}, vx: {json.dumps(vx)}, vy: {json.dumps(vy)}, pulse: {pulse} }},"
        )
    return "const views = [\n" + "\n".join(rows) + "\n      ];"


def main() -> None:
    html = SRC.read_text(encoding="utf-8")
    start = html.find("    const slides = [")
    end = html.find('    document.getElementById("tot")')
    if start < 0 or end < 0:
        raise SystemExit("No encontré el bloque de láminas en la presentación EP2")
    payload = json.dumps(SLIDES, ensure_ascii=False, indent=2)
    html = html[:start] + "    const slides = " + payload + ";\n\n" + html[end:]

    v0 = html.find("            const views = [")
    v1 = html.find("\n      ];", v0)
    if v0 < 0 or v1 < 0:
        raise SystemExit("No encontré el arreglo de cámaras")
    v1 += len("\n      ];")
    html = html[:v0] + "            " + _views_js() + html[v1:]

    html = html.replace(
        "<title>IntegraBot EP2 · Agente funcional</title>",
        "<title>IntegraBot EP3 · Observabilidad</title>",
    )
    html = html.replace(
        "Diego Madrid · IntegraBot EP2 · ISY0101",
        "Diego Madrid · IntegraBot EP3 · ISY0101",
    )
    html = html.replace("Guion EP2 — solo presentador", "Guion EP3 — solo presentador")
    html = html.replace(
        "const DENSE_SLIDE_INDEXES = new Set([9, 13]); /* orquestación + demo (mucho contenido) */",
        "const DENSE_SLIDE_INDEXES = new Set([3, 11]); /* métricas + demo */",
    )
    OUT.write_text(html, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
