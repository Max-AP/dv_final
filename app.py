import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. DATOS
df_raw = pd.read_parquet("dataset_wildchat_etiquetado.parquet")
df_raw["timestamp"] = pd.to_datetime(df_raw["timestamp"], utc=True)

df_raw["duracion_cat"] = pd.cut(
    df_raw["session_length"],
    bins   = [0, 3, 10, 9999],
    labels = ["Corta (1–3)", "Media (4–10)", "Larga (11+)"]
).astype(str)

# 2. CONSTANTES
COLORS = {
    "Memoria de trabajo": "#4A90D9",
    "Memoria episódica":  "#E8874A",
    "Memoria semántica":  "#45B08C",
}
CLASS_ORDER = ["Memoria de trabajo", "Memoria episódica", "Memoria semántica"]
DIAS_ORDER  = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
DIAS_ES     = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

LAYOUT_BASE = dict(
    font_family   = "Calibri",
    paper_bgcolor = "#FAFBFC",
    plot_bgcolor  = "#FAFBFC",
    font_color    = "#374151",
    title_font    = dict(size=14, color="#1B2E45"),
    margin        = dict(t=55, b=40, l=50, r=30),
    legend        = dict(
        orientation = "h",
        yanchor="bottom", y=-0.28,
        xanchor="center", x=0.5,
        font_size=10,
    ),
)

def layout_base(leyenda=True):
    if leyenda:
        return LAYOUT_BASE
    base = {k: v for k, v in LAYOUT_BASE.items() if k != "legend"}
    base["showlegend"] = False
    return base

# 3. APP
app    = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Pulso de Memoria"
server = app.server

# 4. LAYOUT
CARD_STYLE = {"borderRadius": "10px", "boxShadow": "0 2px 8px rgba(0,0,0,0.06)"}

app.layout = dbc.Container([

    # Header
    dbc.Row(dbc.Col([
        html.H2("Pulso de Memoria", className="text-primary mt-4 mb-0",
                style={"fontFamily":"Calibri","fontWeight":"700"}),
        html.P("Dashboard de patrones temporales de memoria en agentes "
               "conversacionales de IA — WildChat-1M",
               className="text-muted mb-3", style={"fontSize":"13px"}),
        html.Hr(),
    ])),

    # Filtros
    dbc.Row([
        dbc.Col([
            html.Label("Capa de memoria",
                       style={"fontSize":"12px","fontWeight":"600"}),
            dcc.Dropdown(
                id="filtro-memoria",
                options=[{"label": c, "value": c} for c in CLASS_ORDER],
                value=CLASS_ORDER,
                multi=True, clearable=False,
                style={"fontSize":"12px"},
            ),
        ], width=4),

        dbc.Col([
            html.Label("Duración de sesión",
                       style={"fontSize":"12px","fontWeight":"600"}),
            dcc.Dropdown(
                id="filtro-duracion",
                options=[
                    {"label": "Corta (1–3 turnos)",  "value": "Corta (1–3)"},
                    {"label": "Media (4–10 turnos)", "value": "Media (4–10)"},
                    {"label": "Larga (11+ turnos)",  "value": "Larga (11+)"},
                ],
                value=["Corta (1–3)", "Media (4–10)", "Larga (11+)"],
                multi=True, clearable=False,
                style={"fontSize":"12px"},
            ),
        ], width=4),

        dbc.Col([
            html.Label("Rango de fechas",
                       style={"fontSize":"12px","fontWeight":"600"}),
            dcc.DatePickerRange(
                id="filtro-fecha",
                min_date_allowed = df_raw["timestamp"].min().date(),
                max_date_allowed = df_raw["timestamp"].max().date(),
                start_date       = df_raw["timestamp"].min().date(),
                end_date         = df_raw["timestamp"].max().date(),
                display_format   = "YYYY-MM-DD",
                style={"fontSize":"12px"},
            ),
        ], width=4),
    ], className="mb-3"),

    # KPIs
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.P("Turnos analizados", className="text-muted mb-1",
                   style={"fontSize":"11px"}),
            html.H4(id="kpi-turnos", className="mb-0 text-primary"),
        ]), style=CARD_STYLE), width=2),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.P("Sesiones únicas", className="text-muted mb-1",
                   style={"fontSize":"11px"}),
            html.H4(id="kpi-sesiones", className="mb-0 text-primary"),
        ]), style=CARD_STYLE), width=2),

        # KPI clave: % trabajo
        dbc.Col(dbc.Card(dbc.CardBody([
            html.P("Memoria de trabajo", className="text-muted mb-1",
                   style={"fontSize":"11px"}),
            html.H4(id="kpi-trabajo", className="mb-0",
                    style={"color": COLORS["Memoria de trabajo"]}),
        ]), style={**CARD_STYLE,
                   "borderLeft": f"4px solid {COLORS['Memoria de trabajo']}"}),
        width=2),

        # KPI clave: % episódica
        dbc.Col(dbc.Card(dbc.CardBody([
            html.P("Memoria episódica", className="text-muted mb-1",
                   style={"fontSize":"11px"}),
            html.H4(id="kpi-episodica", className="mb-0",
                    style={"color": COLORS["Memoria episódica"]}),
        ]), style={**CARD_STYLE,
                   "borderLeft": f"4px solid {COLORS['Memoria episódica']}"}),
        width=2),

        # KPI clave: % trabajo
        dbc.Col(dbc.Card(dbc.CardBody([
            html.P("Memoria semántica", className="text-muted mb-1",
                   style={"fontSize":"11px"}),
            html.H4(id="kpi-semantica", className="mb-0",
                    style={"color": COLORS["Memoria semántica"]}),
        ]), style={**CARD_STYLE,
                   "borderLeft": f"4px solid {COLORS['Memoria semántica']}"}),
        width=2),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.P("Confianza promedio", className="text-muted mb-1",
                   style={"fontSize":"11px"}),
            html.H4(id="kpi-confianza", className="mb-0 text-warning"),
        ]), style=CARD_STYLE), width=2),
    ], className="mb-4"),

    # Fila 1: Línea temporal + Heatmap
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="fig-temporal", config={"displayModeBar": False}),
            width=8,
        ),
        dbc.Col([
            # Selector dedicado para el heatmap
            html.Label("Heatmap — capa a visualizar:",
                       style={"fontSize":"11px","fontWeight":"600",
                              "marginBottom":"4px","display":"block"}),
            dcc.RadioItems(
                id="selector-heatmap",
                options=[{"label": c.replace("Memoria ",""), "value": c}
                         for c in CLASS_ORDER],
                value="Memoria semántica",
                inline=True,
                inputStyle={"marginRight":"3px"},
                labelStyle={"marginRight":"10px","fontSize":"11px"},
            ),
            dcc.Graph(id="fig-heatmap", config={"displayModeBar": False}),
        ], width=4),
    ], className="mb-3"),

    # Fila 2: Confidence + Gapminder
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="fig-confidence", config={"displayModeBar": False}),
            width=4,
        ),
        dbc.Col(
            dcc.Graph(id="fig-gapminder", config={"displayModeBar": False}),
            width=8,
        ),
    ], className="mb-4"),

    # Footer
    html.Hr(),
    html.P("Fuente: WildChat-1M (Allen Institute for AI) · "
           "Clasificador: Sentence Embeddings + Logistic Regression",
           className="text-muted text-center mb-3",
           style={"fontSize":"11px"}),

], fluid=True, style={"backgroundColor":"#F8FAFC"})


# 5. CALLBACK
@app.callback(
    [Output("kpi-turnos",    "children"),
     Output("kpi-sesiones",  "children"),
     Output("kpi-trabajo", "children"),
     Output("kpi-episodica", "children"),   # ← nuevo
     Output("kpi-semantica", "children"),
     Output("kpi-confianza", "children"),
     Output("fig-temporal",  "figure"),
     Output("fig-heatmap",   "figure"),
     Output("fig-confidence","figure"),
     Output("fig-gapminder", "figure")],
    [Input("filtro-memoria",   "value"),
     Input("filtro-duracion",  "value"),
     Input("filtro-fecha",     "start_date"),
     Input("filtro-fecha",     "end_date"),
     Input("selector-heatmap", "value")],  # ← nuevo
)
def actualizar(memorias, duraciones, fecha_ini, fecha_fin, selector_heatmap):

    # Filtrar
    dff = df_raw.copy()
    if memorias:
        dff = dff[dff["memory_layer"].isin(memorias)]
    if duraciones:
        dff = dff[dff["duracion_cat"].isin(duraciones)]
    if fecha_ini and fecha_fin:
        fi = pd.to_datetime(fecha_ini).tz_localize("UTC")
        ff = pd.to_datetime(fecha_fin).tz_localize("UTC") + pd.Timedelta(days=1)
        dff = dff[(dff["timestamp"] >= fi) & (dff["timestamp"] < ff)]

    # KPIs
    kpi_turnos = f"{len(dff):,}"
    kpi_sesiones = f"{dff['session_id'].nunique():,}"

    if not dff.empty:
        n_epis = len(dff[dff["memory_layer"] == "Memoria episódica"])
        n_trab = len(dff[dff["memory_layer"] == "Memoria de trabajo"])
        n_sema = len(dff[dff["memory_layer"] == "Memoria semántica"])
        pct_epis = n_epis / len(dff) * 100
        kpi_episodica = f"{pct_epis:.1f}%"
        pct_trab = n_trab / len(dff) * 100
        kpi_trabajo = f"{pct_trab:.1f}%"
        pct_sema = n_sema / len(dff) * 100
        kpi_semantica = f"{pct_sema:.1f}%"
        kpi_confianza = f"{dff['confidence_score'].mean():.2f}"
    else:
        kpi_episodica = "—"
        kpi_trabajo = "—"
        kpi_semantica = "—"
        kpi_confianza = "—"

    vacio = go.Figure().update_layout(**layout_base(False), title="Sin datos")
    if dff.empty:
        return (kpi_turnos, kpi_sesiones, kpi_trabajo, kpi_episodica, kpi_semantica, kpi_confianza,
                vacio, vacio, vacio, vacio)


    # FIG 1 — Evolución por turno

    MAX_TURNO = 20
    dff_t = dff[dff["turn_number"] <= MAX_TURNO]

    pivot = (
        dff_t.groupby(["turn_number", "memory_layer"]).size()
        .reset_index(name="n")
    )
    pivot["pct"] = pivot.groupby("turn_number")["n"] \
                        .transform(lambda x: x / x.sum() * 100)

    fig1 = go.Figure()
    for capa in CLASS_ORDER:
        if capa not in memorias:
            continue
        d = pivot[pivot["memory_layer"] == capa].sort_values("turn_number")
        fig1.add_trace(go.Scatter(
            x=d["turn_number"], y=d["pct"],
            name=capa, mode="lines+markers",
            line=dict(color=COLORS[capa], width=2.5, shape="spline"),
            marker=dict(size=6, color=COLORS[capa],
                        line=dict(color="white", width=1.5)),
            hovertemplate=(
                f"<b>{capa}</b><br>"
                "Turno %{x}<br>%{y:.1f}%<extra></extra>"
            ),
        ))

    # Anotación clave: línea episódica casi invisible es el hallazgo
    if "Memoria episódica" in memorias:
        fig1.add_annotation(
            x=10, y=3,
            text=(
                "<b>Episódica: ~0.9%</b><br>"
                "Casi inexistente — el sistema<br>"
                "no soporta memoria entre sesiones"
            ),
            showarrow=True, arrowhead=2,
            arrowcolor=COLORS["Memoria episódica"],
            font=dict(size=10, color=COLORS["Memoria episódica"]),
            bgcolor="white",
            bordercolor=COLORS["Memoria episódica"],
            borderwidth=1,
            ax=70, ay=-55,
        )

    fig1.update_layout(
        **layout_base(),
        title="Evolución del tipo de memoria por turno de conversación",
        xaxis=dict(title="Número de turno", gridcolor="#E5E7EB",
                   tickmode="linear", dtick=2, zeroline=False),
        yaxis=dict(title="Proporción (%)", gridcolor="#E5E7EB",
                   zeroline=False, range=[0, 100]),
    )


    # FIG 2 — Heatmap hora × día  (usa selector dedicado)

    capa_heatmap = selector_heatmap  # ← viene del RadioItems

    heat_data = (
        dff[dff["memory_layer"] == capa_heatmap]
        .groupby(["day_of_week", "hour_of_day"]).size()
        .reset_index(name="n")
    )
    total_celda = (
        dff.groupby(["day_of_week", "hour_of_day"]).size()
        .reset_index(name="total")
    )
    heat_data = heat_data.merge(total_celda, on=["day_of_week", "hour_of_day"])
    heat_data["pct"] = (heat_data["n"] / heat_data["total"] * 100).round(1)

    mat = pd.pivot_table(
        heat_data, values="pct",
        index="hour_of_day", columns="day_of_week", fill_value=0,
    ).reindex(columns=DIAS_ORDER, fill_value=0)
    mat.columns = DIAS_ES

    color_hm = COLORS.get(capa_heatmap, "#4A90D9")

    fig2 = go.Figure(go.Heatmap(
        z=mat.values, x=DIAS_ES, y=mat.index.tolist(),
        colorscale=[[0, "#F8FAFC"], [1, color_hm]],
        hovertemplate="<b>%{x} %{y}h</b><br>%{z:.1f}%<extra></extra>",
        colorbar=dict(title="%", thickness=10),
    ))
    fig2.update_layout(
        **layout_base(False),
        title=f"Actividad por hora y día<br>"
              f"<sup>{capa_heatmap}</sup>",
        xaxis=dict(title=""),
        yaxis=dict(title="Hora", autorange="reversed",
                   tickmode="linear", dtick=4),
    )

    # FIG 3 — Confidence por capa

    conf = (
        dff.groupby("memory_layer")["confidence_score"]
        .agg(["mean", "std", "count"])
        .reset_index()
        .sort_values("mean", ascending=True)
    )

    fig3 = go.Figure()
    for _, row in conf.iterrows():
        c = COLORS.get(row["memory_layer"], "#999")
        fig3.add_trace(go.Bar(
            y=[row["memory_layer"].replace("Memoria ", "")],
            x=[row["mean"]],
            orientation="h",
            marker=dict(color=c, opacity=0.85),
            error_x=dict(type="data", array=[row["std"]],
                         color="#9CA3AF", thickness=1.5, width=5),
            hovertemplate=(
                f"<b>{row['memory_layer']}</b><br>"
                f"Media: {row['mean']:.3f}<br>"
                f"n={int(row['count']):,}<extra></extra>"
            ),
            showlegend=False,
        ))
        fig3.add_annotation(
            y=row["memory_layer"].replace("Memoria ", ""),
            x=row["mean"] + row["std"] + 0.01,
            text=f"<b>{row['mean']:.2f}</b>",
            showarrow=False, xanchor="left",
            font=dict(size=11, color=c),
        )

    # Anotación explicativa para episódica
    fig3.add_annotation(
        x=0.62, y=0,      # posición sobre la barra de episódica (la más baja)
        text=(
            "Menor confianza: el corpus<br>"
            "casi no contiene ejemplos<br>"
            "reales de memoria episódica"
        ),
        showarrow=True, arrowhead=2,
        arrowcolor=COLORS["Memoria episódica"],
        font=dict(size=9, color="#6B7280"),
        bgcolor="#FFF5EE",
        bordercolor=COLORS["Memoria episódica"],
        borderwidth=1,
        align="left",
        ax=60, ay=-40,
    )

    fig3.add_vline(
        x=0.333, line_dash="dot", line_color="#D1D5DB",
        annotation_text="Azar", annotation_font_size=8,
        annotation_font_color="#9CA3AF",
    )
    fig3.update_layout(
        **layout_base(False),
        title="Confianza promedio del clasificador",
        xaxis=dict(title="Score de confianza", range=[0.3, 1.0],
                   gridcolor="#E5E7EB", tickformat=".0%", zeroline=False),
        yaxis=dict(gridcolor="#E5E7EB"),
        bargap=0.5,
    )

    # FIG 4 — Gapminder por mes

    # Proporción de cada capa por mes
    df_mes = (
        dff.groupby(["month", "memory_layer"])
        .size()
        .reset_index(name="n")
    )
    df_mes["pct"] = df_mes.groupby("month")["n"] \
        .transform(lambda x: x / x.sum() * 100)

    fig4 = px.area(
        df_mes.sort_values("month"),
        x="month", y="pct",
        color="memory_layer",
        color_discrete_map=COLORS,
        category_orders={"memory_layer": CLASS_ORDER},
        labels={
            "month": "Mes",
            "pct": "Proporción (%)",
            "memory_layer": "Capa de memoria",
        },
        title="Distribución de capas de memoria — estable durante 12 meses",
        groupnorm="percent",
    )
    fig4.update_layout(
        **layout_base(),
        xaxis=dict(title="Mes", gridcolor="#E5E7EB", tickangle=-30),
        yaxis=dict(title="Proporción (%)", gridcolor="#E5E7EB",
                   range=[0, 100]),
    )

    return (kpi_turnos, kpi_sesiones, kpi_trabajo, kpi_episodica, kpi_semantica, kpi_confianza,
             fig1, fig2, fig3, fig4)


# 6. ENTRY POINT
if __name__ == "__main__":
    app.run(debug=True)