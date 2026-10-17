# IntegraBot — Agente funcional de RRHH (EP2)

**Informe técnico · Evaluación Parcial N°2**

| Campo | Dato |
| --- | --- |
| **Asignatura** | ISY0101 — Ingeniería de Soluciones con IA |
| **Autor(es)** | Diego Alejandro Madrid Muñoz · RUT 19.914.672-6 |
| **Docente** | Jaime Andrés Menéndez Silva |
| **Sección** | 011V |
| **Fecha** | 17 de octubre de 2026 |
| **Repositorio** | https://github.com/DeboradorDeMundos/integraservicios-rrhh |

> **Nota:** Borrador en Markdown. Para el AVA exporta a **Word (.docx) o PDF** con el script `python scripts/fill_informe_ep2_docx.py` (misma plantilla y tablas que EP1). Formato APA: ver sección formal en `INFORME_EVA1.md`.

---

## Guía formal (resumen EP2)

| Requisito | Detalle |
| --- | --- |
| **Extensión** | Máximo **5 páginas** de contenido (sin portada, bibliografía aparte si el docente lo permite) |
| **Fuente** | Times New Roman 12 pt · interlineado 1,5 o 2,0 (confirmar con docente) |
| **Entrega** | AVA + correo docente + enlace GitHub |
| **Anexos** | Capturas Streamlit (orquestación, fuentes, ticket INT), salida de `agent_scenarios_test.py` |

---

## Cobertura rúbrica EP2

| IE | Peso | Evidencia en el proyecto |
| --- | --- | --- |
| IE1 Tools autónomas | 10% | `src/agent_tools.py` (4 herramientas) |
| IE2 Framework agente | 10% | LangChain `bind_tools` + ReAct (`src/agent.py`) |
| IE3 Memoria de contenido | 10% | `src/memory.py`, `src/conversation.py` |
| IE4 Recuperación semántica | 10% | `src/retriever.py`, Chroma MMR filtrado |
| IE5 Planificación | 10% | `src/planner.py`, expander *Orquestación del agente* |
| IE6 Informe + diagramas | 10% | Este informe, `docs/diagrama_orquestacion_ep2.png` |
| IE7 Decisiones (oral) | 10% | Demo Streamlit + `presentacion_ep2.html` |
| IE8 Diagrama + README | 10% | README § EP2, scripts de prueba |
| IE9 Justificación | 10% | §4 y §6 de este informe |
| IE10 Lenguaje técnico | 10% | Presentación y defensa con evidencias |

---

## Resumen ejecutivo

IntegraBot evoluciona del **copiloto RAG (EP1)** a un **agente orquestado** para Gestión de Personas de IntegraServicios S.A. El agente integra **consulta documental** (RAG interno/externo), **escritura** (tickets RRHH mock e memoria de caso) y **razonamiento** (clasificación de tareas + plan priorizado). La implementación usa **LangChain** (bucle ReAct con `bind_tools`), memoria corta y larga, y pruebas en `scripts/agent_scenarios_test.py`. Se mantiene la política EP1 de **cero invención** mediante `guardrails.py` y derivación institucional.

---

## 1. Caso organizacional y continuidad EP1 → EP2

### 1.1 Problema y objetivos

| Situación | Impacto |
| --- | --- |
| ~750 consultas/mes a RRHH | Alta carga operativa |
| Consultas repetitivas (beneficios, permisos, normativa) | Demoras y riesgo de respuestas informales |
| Necesidad de trazabilidad legal | Obligación de citar fuentes y escalar lo sensible |

| Objetivo EP2 | Meta |
| --- | --- |
| Autonomía controlada | Elegir cuándo buscar, escribir memoria o abrir ticket |
| Continuidad conversacional | Memoria corta + larga por sesión |
| Trazabilidad | Plan visible, tools ejecutadas, fuentes RAG, ticket INT |
| Herencia EP1 | Mismo corpus dual y guardrails anti-alucinación |

### 1.2 Corpus documental (sin cambios respecto a EP1)

| Tipo | Documento | Uso en el agente |
| --- | --- | --- |
| Interno | `RIOHS_IntegraServicios_2026.pdf` | Tool `buscar_politicas_internas` |
| Interno | `Contrato_Colectivo_2026.pdf` | Tool `buscar_politicas_internas` |
| Externo | `Codigo_del_Trabajo_Chile.pdf` | Tool `buscar_normativa_externa` |

### 1.3 Restricciones de alcance

| Restricción | Descripción |
| --- | --- |
| No es asesoría legal | Orienta con documentos; escala sumarios y litigios |
| Tickets mock | Formato INT-xxxxx en `tickets_local/` |
| Sin SSO / portal RRHH | Demo académica en Streamlit |
| Proveedor LLM | `MODEL_PROVIDER`: google, groq o local (demos sin API) |

---

## 2. Herramientas y framework del agente (IE1, IE2)

### 2.1 Herramientas LangChain

| Herramienta | Tipo | Función |
| --- | --- | --- |
| `buscar_politicas_internas` | Consulta | RIOHS + Contrato (`source_type=interno`) |
| `buscar_normativa_externa` | Consulta | Código / Ley Karin (`source_type=externo`) |
| `guardar_memoria_caso` | Escritura | Hechos en `./case_memory/{session}.json` |
| `registrar_ticket_gestion_personas` | Escritura | Ticket INT en `tickets_local/tickets_rrhh.jsonl` |

### 2.2 Stack tecnológico

| Capa | Tecnología | Archivo / notas |
| --- | --- | --- |
| Orquestación agente | LangChain ReAct, `bind_tools` | `src/agent.py` |
| Planificación | Clasificación + plan numerado | `src/planner.py` |
| RAG | ChromaDB, MMR k=4 | `src/retriever.py`, `src/rag_engine.py` |
| UI | Streamlit + trazas EP2 | `app.py` |
| LLM (producción) | Gemini / Groq | `src/models.py`, `.env` |
| LLM (demo offline) | Generador extractivo local | `src/local_generator.py` |

### 2.3 Flujo ReAct (resumen)

| Paso | Acción |
| --- | --- |
| 1 | `planner.py` clasifica y arma plan → system prompt |
| 2 | LLM invoca tools (hasta 4 turnos) |
| 3 | Tools recuperan fragmentos o persisten memoria/ticket |
| 4 | Síntesis + `guardrails.py` → respuesta con cita o derivación |

---

## 3. Memoria y recuperación semántica (IE3, IE4)

### 3.1 Capas de memoria

| Capa | Mecanismo | Módulo | Parámetro |
| --- | --- | --- | --- |
| Corto plazo | Últimos turnos en prompt | `conversation.py` | `AGENT_HISTORY_LIMIT=8` |
| Largo plazo | Hechos, tema, tickets por sesión | `memory.py` | JSON por `session_id` |
| Semántico | MMR + filtro corpus | `retriever.py` | k=4, `lambda_mult=0.75` |

### 3.2 Parámetros de recuperación (heredados EP1)

| Parámetro | Valor | Justificación |
| --- | --- | --- |
| Retriever | MMR | Relevancia + diversidad de chunks |
| k | 4 | Trazabilidad en expander de fuentes |
| Filtro metadata | `source_type` interno/externo | No mezclar reglamento y ley |
| Índice Google | `./chroma_db_v2` | Embeddings `gemini-embedding-001` |
| Índice local/groq | `./chroma_db_local` / `chroma_db_groq` | Embeddings HuggingFace |

### 3.3 Continuidad demostrable

| Turno | Pregunta ejemplo | Comportamiento esperado |
| --- | --- | --- |
| 1 | Finiquito / sumario / cheque litigioso | Caso sensible → ticket INT + escalamiento |
| 2 | «¿Cuál es el estado del ticket que abrimos?» | Memoria + consulta ticket (estado **abierto**) |

---

## 4. Planificación y decisiones adaptativas (IE5, IE7)

### 4.1 Tipos de tarea (`TaskKind`)

| Clasificación | Criterio (resumen) | Acción principal |
| --- | --- | --- |
| FAQ | Consulta documentada simple | Búsqueda interna + cita |
| Multietapa | Varias subpreguntas / “y además” | Interno ± externo + memoria |
| Sensible | Finiquito, sumario, litigio, cheque | Ticket INT + límites del copiloto |
| Fuera de dominio | Clima, deportes, etc. | Derivación sin RAG |
| Seguimiento | Follow-up con memoria de caso | Memoria ± ticket (no RAG irrelevante) |

### 4.2 Escenarios para demo oral / video

| # | Pregunta | Plan | Evidencia en UI |
| --- | --- | --- | --- |
| 1 | ¿Cuál es el valor del bono de colación? | FAQ | Cita Contrato/RIOHS, fuentes RAG |
| 2 | ¿Días administrativos y qué documentos? | Multietapa | Plan multietapa, memoria |
| 3 | ¿Mañana va a llover? | Fuera de dominio | Derivación, sin inventar |
| 4 | Finiquito litigioso / cheque litigioso | Sensible | INT-xxxxx, texto de escalamiento |
| 5 | ¿Estado del ticket que abrimos? | Seguimiento | Memoria + estado ticket |

---

## 5. Orquestación, pruebas y repositorio (IE6, IE8)

### 5.1 Módulos y responsabilidades

| Módulo | Responsabilidad |
| --- | --- |
| `app.py` | Chat Streamlit, perfil, expander orquestación |
| `agent.py` | `run_agent`, ReAct, fallback local |
| `planner.py` | Clasificación y plan de ejecución |
| `agent_tools.py` | Cuatro tools de consulta/escritura |
| `memory.py` | Persistencia de caso |
| `retriever.py` | Acceso Chroma filtrado |
| `rag_engine.py` | Pipeline recuperación → generación |
| `guardrails.py` | Validación post-respuesta (EP1) |
| `tickets.py` | Cliente mock INT-xxxxx |

### 5.2 Diagrama

Ver **Figura 1** en Word/PDF: `docs/diagrama_orquestacion_ep2.png` (generado con `scripts/render_diagram_ep2.py`).

### 5.3 Pruebas y comandos

| Script | Modo | Qué valida |
| --- | --- | --- |
| `scripts/smoke_test.py` | Offline / `--live` | Regresión corpus RAG EP1 |
| `scripts/agent_scenarios_test.py` | Offline | Planner, memoria, sensible, dominio |
| `scripts/agent_scenarios_test.py --live` | Con API | Tools + LLM |
| `streamlit run app.py` | Manual | Demo integral + capturas AVA |

```bash
python generate_data.py
python scripts/smoke_test.py
python scripts/agent_scenarios_test.py
streamlit run app.py
```

### 5.4 Entrega AVA (checklist)

| # | Acción |
| --- | --- |
| 1 | Completar conclusión y reflexión **sin IA** |
| 2 | Exportar informe Word/PDF (≤ 5 páginas cuerpo) |
| 3 | Adjuntar capturas (orquestación, fuentes, ticket) |
| 4 | Subir AVA + enlace GitHub |
| 5 | Enviar correo al docente |
| 6 | Presentación oral + demo en vivo |

---

## 6. Justificación de componentes (IE9)

| Decisión | Motivo |
| --- | --- |
| ReAct + tools vs. cadena fija EP1 | EP2 exige autonomía con consulta y escritura |
| Dos retrievers filtrados | Separar política interna y normativa externa |
| Memoria JSON por sesión | Flujos multietapa sin inflar tokens |
| Tickets mock INT | Escritura auditable y reproducible |
| Guardrails EP1 preservados | No relajar cumplimiento por tener agente |
| `MODEL_PROVIDER=local` | Demos cuando la cuota Gemini está agotada |

---

## 7. Conclusión

_[Redactar en tus palabras, sin IA: qué aporta el agente a IntegraServicios, qué aprendiste sobre planificación/memoria/tools, y cómo se relaciona con el EP1.]_

### Reflexión individual — Diego Alejandro Madrid Muñoz

_[8–12 líneas sin IA: tu rol, dificultades (cuota API, casos sensibles, demo), aprendizaje.]_

---

## 8. Declaración de uso de IA

Se empleó IA generativa (Cursor IDE, Google Gemini API) como apoyo en código, documentación, diagramas y presentación HTML. El análisis del caso, las decisiones de diseño, las conclusiones y la reflexión individual son responsabilidad del autor. Duoc UC (2025): https://bibliotecas.duoc.cl/ia

---

## 9. Referencias (APA)

Google. (2026). *Gemini API documentation*. https://ai.google.dev/

LangChain. (2026). *LangChain Python documentation*. https://python.langchain.com/

Chroma. (2026). *ChromaDB documentation*. https://docs.trychroma.com/

Streamlit. (2026). *Streamlit documentation*. https://docs.streamlit.io/

Duoc UC. (2025). *Uso de inteligencia artificial en el aprendizaje*. https://bibliotecas.duoc.cl/ia
