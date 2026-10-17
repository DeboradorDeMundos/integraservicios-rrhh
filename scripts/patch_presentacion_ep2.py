#!/usr/bin/env python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "presentacion_ep2.html"
text = p.read_text(encoding="utf-8")
text = text.replace(
    "<title>IntegraBot · IntegraServicios S.A.</title>",
    "<title>IntegraBot EP2 · Agente funcional</title>",
)
text = text.replace(
    'SLIDE <span id="sl">01</span>/<span id="tot">16</span>',
    'SLIDE <span id="sl">01</span>/<span id="tot">10</span>',
)
text = text.replace(
    "Diego Madrid · IntegraBot · IntegraServicios S.A.",
    "Diego Madrid · IntegraBot EP2 · ISY0101",
)

start = text.index("const slides = [")
end = text.index('];\n\n    document.getElementById("tot")')

slides = r'''
const slides = [
      {
        html: `
          <div class="logo rise">IB</div>
          <div class="kicker rise">Evaluación Parcial N°2 · ISY0101</div>
          <h1 class="rise">Agente IntegraBot</h1>
          <p class="lead rise">De copiloto RAG a agente con herramientas: consulta, escritura de tickets, memoria de caso y planificación priorizada.</p>
          <div class="rise" style="margin-top:14px">
            <span class="chip">Diego Alejandro Madrid Muñoz</span>
            <span class="chip">LangChain Tools · Chroma · Gemini</span>
          </div>
        `,
        time: "0:00 – 0:50",
        note: "EP2: agente funcional sobre IntegraServicios. Herramientas, memoria, planificación, orquestación, pruebas y demo con decisiones adaptativas."
      },
      {
        html: `
          <div class="kicker">Rúbrica EP2</div>
          <h2 class="rise">Indicadores IE1–IE10</h2>
          <table>
            <tr><th>Encargo (informe + repo)</th><th>Presentación oral</th></tr>
            <tr><td>IE1 Tools · IE2 Framework · IE3 Memoria · IE4 Semántica · IE5 Plan · IE6 Informe</td><td>IE7 Decisiones · IE8 Diagrama+README · IE9 Justificación · IE10 Comunicación técnica</td></tr>
          </table>
        `,
        time: "0:50 – 1:20",
        note: "35% del ramo. 10 min expo + 10 min preguntas."
      },
      {
        html: `
          <div class="kicker">EP1 → EP2</div>
          <h2 class="rise">RAG lineal → agente orquestado</h2>
          <div class="row-2">
            <div class="card"><h3>EP1</h3><p>Retrieve → generate → guardrails</p></div>
            <div class="card"><h3>EP2</h3><p>Planner + tools ReAct + memoria + tickets INT</p></div>
          </div>
        `,
        time: "1:20 – 2:00",
        note: "RAG queda dentro de tools buscar_interno y buscar_externo."
      },
      {
        html: `
          <div class="kicker">IE1 · IE2</div>
          <h2 class="rise">Cuatro herramientas</h2>
          <div class="row-4">
            <div class="card"><h3>buscar_politicas_internas</h3></div>
            <div class="card"><h3>buscar_normativa_externa</h3></div>
            <div class="card"><h3>guardar_memoria_caso</h3></div>
            <div class="card"><h3>registrar_ticket_rrhh</h3></div>
          </div>
        `,
        time: "2:00 – 2:45",
        note: "LangChain bind_tools + bucle ReAct en agent.py."
      },
      {
        html: `
          <div class="kicker">IE3 · IE4</div>
          <h2 class="rise">Memoria dual + Chroma</h2>
          <div class="row">
            <div class="card"><h3>Corto</h3><p>8 turnos</p></div>
            <div class="card"><h3>Largo</h3><p>case_memory JSON</p></div>
            <div class="card"><h3>Semántico</h3><p>MMR + filter interno/externo</p></div>
          </div>
        `,
        time: "2:45 – 3:30",
        note: "Continuidad en flujos prolongados y follow-ups."
      },
      {
        html: `
          <div class="kicker">IE5 · IE7</div>
          <h2 class="rise">Planificación adaptativa</h2>
          <p class="lead">planner.py: FAQ · multietapa · sensible · fuera de dominio · seguimiento</p>
          <p class="sub">Visible en expander Orquestación del agente (Streamlit).</p>
        `,
        time: "3:30 – 4:15",
        note: "Ejemplo: clima deriva; sumario crea ticket INT."
      },
      {
        html: `
          <div class="kicker">IE8</div>
          <h2 class="rise">Orquestación</h2>
          <p class="lead">app.py → run_agent → planner → tools → rag_engine → guardrails</p>
          <p class="sub">Diagrama: docs/diagrama_orquestacion_ep2.png · README en GitHub</p>
        `,
        time: "4:15 – 5:00",
        note: "Justificar módulos IE9 en informe Word."
      },
      {
        html: `
          <div class="kicker">Demo IE7</div>
          <h2 class="rise">localhost:8501</h2>
          <div class="card"><p>1) Colación · 2) Multietapa · 3) Clima · 4) Caso sensible + ticket</p></div>
        `,
        time: "5:00 – 8:30",
        note: "DEMO EN VIVO con expanders de plan y fuentes RAG."
      },
      {
        html: `
          <div class="kicker">Evidencias IE6</div>
          <h2 class="rise">Pruebas reproducibles</h2>
          <p class="mono">python scripts/agent_scenarios_test.py</p>
          <p class="mono">python scripts/smoke_test.py --live</p>
        `,
        time: "8:30 – 9:15",
        note: "Capturas para AVA + repo actualizado."
      },
      {
        html: `
          <div class="kicker">Cierre IE10</div>
          <h2 class="rise">Planifica · recuerda · consulta · escribe · deriva</h2>
          <p class="sub">Gracias — preguntas técnicas.</p>
        `,
        time: "9:15 – 10:00",
        note: "Mencionar declaración IA Duoc y reflexión individual propia."
      }
    ]
'''

text = text[:start] + slides.strip() + text[end:]

vstart = text.index("const views = [")
vend = text.index("];\n      let cam = { ...views[0] };")
views = '''
      const views = [
        { name: "INICIO", x: 0, y: 18, z: 40, ry: 0.04, rx: 0.22, rz: 0, zoom: 0.72, vx: "50%", vy: "46%", pulse: 1.0 },
        { name: "RUBRICA", x: 80, y: -20, z: -10, ry: 0.55, rx: 0.15, rz: 0.03, zoom: 1.0, vx: "58%", vy: "42%", pulse: 1.05 },
        { name: "EP2", x: -60, y: 30, z: 20, ry: -0.4, rx: 0.1, rz: 0, zoom: 1.15, vx: "42%", vy: "50%", pulse: 1.1 },
        { name: "TOOLS", x: 40, y: 8, z: -25, ry: 0.35, rx: 0.12, rz: 0.05, zoom: 1.25, vx: "48%", vy: "44%", pulse: 1.2 },
        { name: "MEM", x: 20, y: -12, z: 10, ry: 0.2, rx: 0.18, rz: 0, zoom: 1.35, vx: "52%", vy: "40%", pulse: 1.15 },
        { name: "PLAN", x: 10, y: 5, z: 0, ry: 0.12, rx: 0.06, rz: 0, zoom: 1.5, vx: "50%", vy: "48%", pulse: 1.25 },
        { name: "ORQ", x: 55, y: -18, z: -20, ry: 0.48, rx: 0.2, rz: 0, zoom: 1.4, vx: "54%", vy: "42%", pulse: 1.18 },
        { name: "DEMO", x: 8, y: 4, z: 8, ry: 0.15, rx: 0.05, rz: 0, zoom: 2.0, vx: "50%", vy: "48%", pulse: 1.5 },
        { name: "TEST", x: 90, y: 30, z: 50, ry: 0.7, rx: 0.12, rz: 0.05, zoom: 1.1, vx: "62%", vy: "48%", pulse: 1.05 },
        { name: "FIN", x: 0, y: 25, z: 75, ry: 0.1, rx: 0.28, rz: 0, zoom: 0.65, vx: "50%", vy: "38%", pulse: 0.85 }
      ]
'''
text = text[:vstart] + views.strip() + text[vend:]
p.write_text(text, encoding="utf-8")
print("OK presentacion_ep2.html")
