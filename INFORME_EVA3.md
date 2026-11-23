# IntegraBot — Observabilidad del agente (EP3)

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
| Precisión | 100 % |
| Consistencia (Jaccard) | 100 % |
| Errores | 0 % |
| Latencia p50 / p95 / máx | 71 ms / 145 ms / 12588 ms |
| SLO 5 s | 97 % |
| Ley Karin, Jaccard antes → después | 84 % → 100 % |

La medición inicial está en `observability/ep3_summary_antes.json`. La medición posterior al desempate de cita está en `observability/ep3_summary.json`.

## Cómo reproducir

```bash
python scripts/observability_eval.py
python scripts/render_diagram_ep3.py
python scripts/build_ep3_entregables.py
streamlit run dashboard.py
```
