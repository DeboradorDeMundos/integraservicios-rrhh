# IntegraBot — Copiloto RAG de RRHH y Cumplimiento Laboral

Sistema de **Retrieval-Augmented Generation (RAG)** para **IntegraServicios S.A.** El asistente **IntegraBot** responde consultas de colaboradores sobre el Reglamento Interno (RIOHS), el Contrato Colectivo y extractos del Código del Trabajo / Ley Karin, **citando la fuente** y **sin inventar** montos, plazos ni artículos.

| Dato | Valor |
| --- | --- |
| **Autor** | Diego Madrid |
| **GitHub** | [DeboradorDeMundos](https://github.com/DeboradorDeMundos) |
| **Repositorio** | [integraservicios-rrhh](https://github.com/DeboradorDeMundos/integraservicios-rrhh) |
| **Asignatura** | INGENIERIA DE SOLUCIONES CON INTELIGENCIA ARTIFICIAL_011V_OLS |
| **Proyecto** | EP1 RAG + **EP2 Agente funcional** · RRHH y cumplimiento laboral |

---

## 1. Diagnóstico organizacional y propuesta de valor (IE1)

Gestión de Personas de IntegraServicios S.A. recibe del orden de **750 tickets mensuales** (beneficios, permisos, reglamento, normativa). Gran parte son consultas repetitivas que hoy esperan cola humana, con riesgo de respuestas informales o desactualizadas.

| Problema actual | Meta del copiloto |
| --- | --- |
| Alta carga operativa en RRHH (≈750 tickets/mes) | Autogestión de consultas frecuentes 24/7 |
| Latencia de días en respuestas rutinarias | Respuesta objetivo **< 5 segundos** (índice local + Gemini 2.5 Flash) |
| Riesgo de alucinación jurídica | **0% invención**: si no está en el contexto, se deriva a Gestión de Personas |

IntegraBot no reemplaza a RRHH en casos complejos (finiquitos litigiosos, sumarios, etc.): los **escala** con la frase institucional de derivación.

---

## 2. Arquitectura desacoplada (IE4)

La interfaz, el motor RAG y los datos viven en módulos separados.

```mermaid
flowchart TD
    A[Colaborador en Streamlit app.py] --> B[src/conversation.py historial acotado]
    A --> C[src/rag_engine.py RAGPipeline]
    C --> D[src/ingestion.py corpus interno + externo]
    D --> E[PyPDF ./data + metadata source_type]
    E --> F[RecursiveCharacterTextSplitter 500 / 50]
    F --> G[Google Embeddings + ChromaDB ./chroma_db_v2]
    G --> H[Retriever MMR k=4]
    H --> I[src/prompts.py System Prompt]
    I --> J[Gemini 2.5 Flash]
    J --> K[src/guardrails.py validación]
    K --> A
    A --> L[Expander: fragmentos + corpus interno/externo]
```

Flujo:

1. `generate_data.py` crea PDFs internos (RIOHS, Contrato Colectivo) y externos (Código del Trabajo / Ley Karin).
2. `src/ingestion.py` fragmenta, etiqueta `source_type` (interno/externo) e indexa en ChromaDB local.
3. Cada pregunta recupera 4 fragmentos (MMR), inyecta historial reciente y Gemini responde **solo** con ese contexto.
4. `src/guardrails.py` valida citas o fuerza derivación institucional.
5. `app.py` muestra la respuesta, las citas y el expander de trazabilidad por tipo de corpus.

```
integraservicios-rrhh/
├── data/                         # Corpus dual (interno + externo)
├── scripts/
│   ├── smoke_test.py             # Validación EP1 (IE1–IE4)
│   └── agent_scenarios_test.py   # Escenarios EP2 (plan, memoria, agente)
├── src/
│   ├── __init__.py
│   ├── config.py                 # Caso org. + parámetros RAG/agente
│   ├── ingestion.py              # Carga, etiquetado, ChromaDB
│   ├── retriever.py              # Retrievers MMR filtrados interno/externo
│   ├── conversation.py           # Memoria corta (historial acotado)
│   ├── memory.py                 # Memoria larga de caso (JSON por sesión)
│   ├── planner.py                # Planificación y clasificación de tareas
│   ├── agent_tools.py            # Tools LangChain (consulta/escritura)
│   ├── agent.py                  # Orquestador agente EP2
│   ├── agent_prompts.py          # System prompt del agente
│   ├── tickets.py                # Tickets RRHH mock (INT-xxxxx)
│   ├── prompts.py                # Prompt RAG + anti-alucinación
│   ├── guardrails.py             # Validación post-respuesta
│   ├── rag_engine.py             # Pipeline RAG (usado por tools)
│   └── errors.py                 # Mensajes de error para el usuario
├── app.py                        # Chat + trazabilidad agente/plan/fuentes
├── generate_data.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 3. Agente funcional EP2 (ISY0101)

IntegraBot **no es solo RAG**: implementa un agente con **LangChain tools** (`bind_tools` + bucle ReAct).

| Requisito EP2 | Implementación |
| --- | --- |
| Consulta | `buscar_politicas_internas`, `buscar_normativa_externa` |
| Escritura | `registrar_ticket_gestion_personas`, `guardar_memoria_caso` |
| Razonamiento | `planner.py` (plan priorizado) + decisión de tools |
| Memoria corta | Historial reciente en prompt (`conversation.py`) |
| Memoria larga | `./case_memory/{session_id}.json` |
| Recuperación semántica | Chroma MMR + filtros `source_type` |
| Trazabilidad UI | Expander *Orquestación del agente (EP2)* |

```mermaid
flowchart LR
    U[Usuario] --> A[agent.run_agent]
    A --> P[planner]
    P --> T[Tools LangChain]
    T --> R[RAG / Chroma]
    T --> M[memory.py]
    T --> K[tickets_rrhh.jsonl]
    T --> A
    A --> U
```

Pruebas EP2:

```bash
python scripts/agent_scenarios_test.py
python scripts/agent_scenarios_test.py --live
```

Guía de informe (5 páginas): ver `INFORME_EVA2.md` en el repo local (plantilla de contenido).

---

## 4. Ingeniería de prompts (IE2)

El System Prompt (`src/prompts.py`) usa `PromptTemplate` de LangChain con:

- **Rol:** IntegraBot, Copiloto de RRHH y Cumplimiento Laboral de IntegraServicios S.A.
- **Inyección triple:** `{context}` + `{question}` + `{chat_history}` (últimas 3 interacciones).
- **Anti-alucinación:** si el dato no está explícito en el contexto, responde **exactamente**:

> No dispongo de la información oficial en los manuales de la empresa ni en el Código del Trabajo para responder con certeza. He derivado tu consulta al equipo de Gestión de Personas.

- **Citación estricta:** `[Fuente: RIOHS_IntegraServicios_2026.pdf, Art. 12]`

---

## 5. Pipeline RAG dual (IE3)

| Capa | Implementación |
| --- | --- |
| Carga | `src/ingestion.py` → `PyPDFDirectoryLoader("./data")` |
| Etiquetado | Metadata `source_type`: `interno` / `externo` por archivo |
| Chunking | `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)` con separadores `Artículo` / `Cláusula` |
| Embeddings | `GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")` |
| Vector store | ChromaDB persistente en `./chroma_db_v2` |
| Retriever | MMR, `k=4`, `lambda_mult=0.75` |
| LLM | `ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)` |

Corpus dual:

| Tipo | Archivo | Contenido mínimo de rúbrica |
| --- | --- | --- |
| Interno | `RIOHS_IntegraServicios_2026.pdf` | Jornadas, licencias médicas, EPP, denuncia Ley Karin |
| Interno | `Contrato_Colectivo_2026.pdf` | Aguinaldo Fiestas Patrias, bono de escolaridad, días administrativos pagados |
| Externo | `Codigo_del_Trabajo_Chile.pdf` | Descanso dominical, finiquitos, horas extraordinarias + Ley Karin |

**Nota de embeddings:** la API de Google ya no sirve `models/embedding-001` (HTTP 404). El proyecto usa el sucesor oficial `gemini-embedding-001`, compatible con Google AI Studio.

---

## 6. Requisitos

- Python 3.10 o superior
- Clave gratuita de [Google AI Studio](https://aistudio.google.com/apikey) (`GOOGLE_API_KEY`)

---

## 7. Instalación

```bash
git clone https://github.com/DeboradorDeMundos/integraservicios-rrhh.git
cd integraservicios-rrhh
```

Entorno virtual:

```bash
python -m venv venv

# Windows
venv\Scripts\activate
# si python no se reconoce: py -m venv venv

# macOS / Linux
source venv/bin/activate
```

Dependencias (`langchain-google-genai` / `google-genai`):

```bash
pip install -r requirements.txt
```

---

## 8. Configuración de la API Key

```bash
# Windows (PowerShell)
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Contenido de `.env`:

```
GOOGLE_API_KEY=tu_api_key_de_google_ai_studio
```

El archivo `.env` **no se sube a GitHub** (está en `.gitignore`, junto con `venv/` y `chroma_db_v2/`).

---

## 9. Ejecución

```bash
python generate_data.py
streamlit run app.py
```

La primera indexación puede tardar unos segundos. Las siguientes reutilizan `./chroma_db_v2`. La UI queda en [http://localhost:8501](http://localhost:8501).

Validación automatizada del código (rúbrica IE1–IE4):

```bash
python scripts/smoke_test.py
python scripts/smoke_test.py --live
```

---

## 10. Trazabilidad en la interfaz

Bajo cada respuesta hay un expander:

**Ver fuentes documentales consultadas (RAG)**

Muestra el PDF de origen, el número de página y el fragmento exacto recuperado de ChromaDB. Si Gemini no tiene evidencia, no cita datos inventados: deriva a Gestión de Personas.

Preguntas de demostración:

- ¿Cuál es el valor del bono de colación?
- ¿Cuántos días administrativos pagados tengo?
- ¿Cuánto es el bono de escolaridad?
- ¿Cómo se denuncian hechos de acoso laboral?
- ¿Cómo se calculan las horas extraordinarias?
- ¿Mañana va a llover? ← debe derivar, no inventar el clima

---

## 11. Errores visibles vs. técnicos

La UI no muestra tracebacks. `src/errors.py` traduce fallas de red, cupo, clave o documentos faltantes a avisos institucionales, con botón de reintento. El detalle técnico queda en la consola.

---

## Autoría y licencia de uso académico

Proyecto de evaluación desarrollado por **Diego Madrid** ([@DeboradorDeMundos](https://github.com/DeboradorDeMundos)) para la asignatura **INGENIERIA DE SOLUCIONES CON INTELIGENCIA ARTIFICIAL_011V_OLS**.

Los PDFs son **simulados** y no sustituyen el texto oficial del Código del Trabajo ni los instrumentos reales de la empresa.
