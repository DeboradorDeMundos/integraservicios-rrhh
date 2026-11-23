"""
Dashboard de observabilidad EP3 — IntegraBot.

Lee los JSONL de observability/ y muestra precisión, latencia, consistencia,
errores, recursos, trazas y recomendaciones.

    streamlit run dashboard.py
"""
from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from src.observability import CHAT_LOG, EVAL_LOG, analyze, load_events

st.set_page_config(
    page_title="IntegraBot | Observabilidad",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&display=swap');
        html, body, [class*="css"], .stApp { font-family: "DM Sans", "Segoe UI", sans-serif; }
        .block-container { padding-top: 1.2rem; max-width: 1180px; }
        .hero {
            background: linear-gradient(135deg, #071A30 0%, #0B5CAB 72%, #1A7AD4 100%);
            color: #fff; border-radius: 18px; padding: 1.2rem 1.4rem 1.1rem;
            margin-bottom: 0.8rem;
        }
        .hero h1 { color: #fff; font-size: 1.7rem; margin: 0 0 0.25rem 0; }
        .hero p { color: #E6F0FA; margin: 0; }
        .finding {
            background: #F4F8FC; border-left: 4px solid #0B5CAB;
            border-radius: 8px; padding: 0.65rem 0.9rem; margin-bottom: 0.45rem;
        }
        .rec {
            background: #fff; border: 1px solid #D5E3F2; border-radius: 12px;
            padding: 0.8rem 1rem; margin-bottom: 0.55rem;
        }
        .rec h4 { margin: 0 0 0.3rem 0; color: #071A30; }
        .rec p { margin: 0; color: #334155; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Observabilidad de IntegraBot</h1>
        <p>Precisión, latencia, consistencia, errores y recursos del agente de Gestión de Personas. Evaluación Parcial N°3.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=15)
def _load(selected: tuple[str, ...]) -> list[dict]:
    return load_events(*selected)


with st.sidebar:
    st.markdown("### Fuentes")
    available = []
    chosen = []
    for name, label in (
        (EVAL_LOG, "Batería EP3"),
        (CHAT_LOG, "Chat en vivo"),
    ):
        available.append(name)
        if st.checkbox(label, value=(name == EVAL_LOG), key=name):
            chosen.append(name)
    st.caption("La batería se genera con `python scripts/observability_eval.py`.")
    st.divider()
    st.markdown("**SLO de respuesta**")
    st.caption("5 segundos por consulta, heredado del caso organizacional.")
    st.caption("El registro no guarda RUT ni correo.")
    if st.button("Actualizar", width="stretch"):
        st.cache_data.clear()

records = _load(tuple(chosen))
if not records:
    st.info(
        "Todavía no hay registros en las fuentes marcadas. "
        "Ejecuta `python scripts/observability_eval.py` y pulsa Actualizar."
    )
    st.stop()

report = analyze(records)
metrics = report["metrics"]
lat = metrics["latency_ms"]

c1, c2, c3, c4, c5 = st.columns(5)
precision = metrics["precision"]
c1.metric("Precisión", "—" if precision is None else f"{precision:.0%}", help="Turnos etiquetados que cumplen la conducta esperada.")
consistency = metrics["consistency"]
c2.metric("Consistencia", "—" if consistency is None else f"{consistency:.0%}", help="Jaccard medio entre respuestas de la misma intención.")
c3.metric("Errores", f"{metrics['error_rate']:.0%}", f"{metrics['error_count']} fallos")
c4.metric("Latencia p95", f"{lat['p95']:.0f} ms", f"media {lat['mean']:.0f} ms")
c5.metric("Cumple SLO", f"{metrics['slo_compliance']:.0%}", f"pico RAM {metrics['peak_kb']['max']:.0f} KB")

frame = pd.DataFrame(records)
frame["preciso_txt"] = frame["precise"].map({True: "sí", False: "no"}).fillna("chat")
frame["latencia_s"] = frame["latency_ms"] / 1000

left, right = st.columns((1.35, 1))
with left:
    st.subheader("Latencia por turno")
    chart = frame[["ts", "latency_ms", "intent", "task_kind"]].copy()
    chart["turno"] = range(1, len(chart) + 1)
    st.line_chart(chart, x="turno", y="latency_ms", height=280)
    st.caption(f"Línea de SLO: {int(metrics['slo_ms'])} ms. El primer punto suele incluir la carga del índice.")
with right:
    st.subheader("Latencia media por tipo de tarea")
    warm = frame[frame["phase"] == "warm"] if "phase" in frame.columns else frame.iloc[1:]
    if warm.empty:
        warm = frame
    kind = (
        warm.groupby("task_kind", dropna=False)["latency_ms"]
        .mean()
        .reset_index()
        .rename(columns={"latency_ms": "media_ms"})
    )
    st.bar_chart(kind, x="task_kind", y="media_ms", height=280)
    st.caption("Medias de turnos tibios. El arranque en frío queda en el gráfico de la izquierda.")

st.subheader("Consistencia por intención")
cons = pd.DataFrame(metrics["consistency_by_intent"])
if cons.empty:
    st.caption("Hacen falta al menos dos turnos de la misma intención.")
else:
    st.bar_chart(cons, x="intent", y="jaccard", height=260)
    st.dataframe(cons, width="stretch", hide_index=True)

st.subheader("Precisión por conducta esperada")
by_expect = metrics["precision_by_expect"]
if by_expect:
    expect_frame = pd.DataFrame(
        [{"conducta": key, "aciertos": val["ok"], "total": val["n"], "tasa": val["rate"]} for key, val in by_expect.items()]
    )
    st.dataframe(expect_frame, width="stretch", hide_index=True)
else:
    st.caption("Los turnos de chat libre no traen etiqueta de precisión.")

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Hallazgos en los registros")
    for line in report["findings"]:
        st.markdown(f'<div class="finding">{html.escape(line)}</div>', unsafe_allow_html=True)
with col_b:
    st.subheader("Recomendaciones")
    for rec in report["recommendations"]:
        st.markdown(
            f'<div class="rec"><h4>{html.escape(rec["titulo"])}</h4>'
            f"<p>{html.escape(rec['detalle'])}</p>"
            f'<p><em>Evidencia: {html.escape(rec["evidencia"])}</em></p></div>',
            unsafe_allow_html=True,
        )

st.subheader("Registro de ejecución")
view = frame[
    [
        "ts",
        "suite",
        "intent",
        "task_kind",
        "expect",
        "latency_ms",
        "cpu_ms",
        "peak_kb",
        "preciso_txt",
        "error",
        "tools",
        "question",
    ]
].copy()
view["tools"] = view["tools"].apply(lambda tools: ", ".join(tools or []))
st.dataframe(view, width="stretch", hide_index=True, height=360)

def _turn_label(run_id: str) -> str:
    row = frame.loc[frame["run_id"] == run_id].iloc[0]
    intent = row["intent"] or row["task_kind"] or "turno"
    return f"{intent} · {row['latency_ms']:.0f} ms · {str(row['question'])[:48]}"


with st.expander("Inspeccionar un turno"):
    options = list(frame["run_id"])
    picked = st.selectbox("Turno", options, format_func=_turn_label)
    row = frame.loc[frame["run_id"] == picked].iloc[0]
    st.write(row["question"])
    st.write(row["answer_excerpt"])
    st.json(
        {
            "eventos": row["events"],
            "plan": row["plan"],
            "citas": row["citations"],
            "tickets": row["ticket_ids"],
            "fuentes": row["source_files"],
            "derivado": bool(row["derived"]),
            "error": row["error"],
        }
    )

st.caption(
    "IntegraServicios S.A. · IntegraBot · la telemetría es local, agregada y sin datos personales. "
    "No reemplaza la revisión humana de casos sensibles."
)
