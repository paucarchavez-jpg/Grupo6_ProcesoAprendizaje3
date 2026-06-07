import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import re

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y CSS (BENTO GRID STYLE)
# ==============================================================================
st.set_page_config(
    page_title="IA en Salud Materno-Infantil | Análisis",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        /* Estilos generales y tipografía */
        .stApp { background-color: #0b0f19; color: #f3f4f6; }
        section[data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1f2937; }
        
        /* Modificadores para el Bento Grid nativo de Streamlit */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px !important;
            border: 1px solid #1f2937 !important;
            background-color: #111827 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s ease-in-out;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #374151 !important;
        }

        /* Tarjetas de Métricas (KPIs) */
        .kpi-title { font-size: 0.9rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 5px;}
        .kpi-value { font-size: 2.5rem; font-weight: 700; color: #ffffff; line-height: 1.2;}
        .kpi-highlight { color: #8b5cf6; } /* Color de acento púrpura */
        
        /* Textos explicativos (Empatía con el usuario) */
        .user-guide { font-size: 0.95rem; color: #d1d5db; border-left: 3px solid #06b6d4; padding-left: 10px; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. PROCESAMIENTO DE DATOS
# ==============================================================================
@st.cache_data
def load_and_process_data():
    df = pd.read_csv("scopus_PA3.csv")
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(0).astype(int)
    df['Cited by'] = pd.to_numeric(df['Cited by'], errors='coerce').fillna(0).astype(int)
    df['Title'] = df['Title'].fillna("Sin título")
    df['Source title'] = df['Source title'].fillna("Desconocido")
    df['Access_Type'] = df['Open Access'].apply(
        lambda x: "Open Access" if pd.notnull(x) and "Open Access" in str(x) else "Restringido"
    )
    return df

try:
    df_raw = load_and_process_data()
except FileNotFoundError:
    st.error("Error: El archivo 'scopus_PA3.csv' no fue encontrado.")
    st.stop()

# ==============================================================================
# 3. INTERFAZ DE USUARIO: BARRA LATERAL (CONTROLES AMPLIADOS)
# ==============================================================================
st.sidebar.markdown("<h2 style='color:#ffffff;'>Panel de Control</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color:#9ca3af; font-size:0.85rem;'>Utilice estos filtros para explorar la bibliografía específica.</p>", unsafe_allow_html=True)

# Nuevo Input: Búsqueda Semántica
search_term = st.sidebar.text_input(
    "🔍 Búsqueda por palabra clave", 
    placeholder="Ej: prediction, risk, neural...",
    help="Filtra los artículos que contengan este término en su título."
)

# Filtro: Rango Temporal
min_year, max_year = int(df_raw['Year'].min()), int(df_raw['Year'].max())
selected_years = st.sidebar.slider(
    "📅 Ventana de Tiempo", min_year, max_year, (min_year, max_year),
    help="Seleccione el rango de años de publicación a analizar."
)

# Nuevo Input: Filtro por Revista (Source title)
journal_options = sorted(df_raw['Source title'].unique().tolist())
selected_journals = st.sidebar.multiselect(
    "📓 Revistas / Conferencias", options=journal_options, default=[],
    placeholder="Todas las fuentes...",
    help="Filtre publicaciones de revistas específicas."
)

# Filtros: Citas y Acceso
min_citations = st.sidebar.number_input("📈 Mínimo de Citas", min_value=0, value=0, step=5, help="Excluir artículos con bajo impacto.")
access_options = df_raw['Access_Type'].unique().tolist()
selected_access = st.sidebar.multiselect("🔓 Tipo de Acceso", options=access_options, default=access_options)

# Aplicación del pipeline de filtros
df_filtered = df_raw[
    (df_raw['Year'] >= selected_years[0]) & 
    (df_raw['Year'] <= selected_years[1]) &
    (df_raw['Cited by'] >= min_citations) &
    (df_raw['Access_Type'].isin(selected_access))
]

if search_term:
    df_filtered = df_filtered[df_filtered['Title'].str.contains(search_term, case=False, na=False)]

if selected_journals:
    df_filtered = df_filtered[df_filtered['Source title'].isin(selected_journals)]

# ==============================================================================
# 4. CUERPO PRINCIPAL: DISEÑO BENTO GRID Y EMPATÍA
# ==============================================================================
st.title("Tendencias de Investigación sobre IA y Machine Learning en Salud Materna e Infantil")

st.markdown("""
<div class="user-guide">
<strong>Pregunta de investigación:</strong>
¿Cuáles son las principales tendencias y áreas de investigación sobre inteligencia artificial y aprendizaje automático en la salud materna e infantil?
<br><br>
<strong>Descripción del dashboard:</strong>
Este dashboard bibliométrico permite analizar la evolución de la investigación científica relacionada con la inteligencia artificial y el aprendizaje automático en el ámbito de la salud materna e infantil.
A través de indicadores de producción científica, citaciones, acceso abierto y análisis temático, es posible identificar los enfoques más estudiados, los trabajos con mayor impacto académico y las tendencias emergentes.
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("⚠️ No hay documentos que coincidan con los filtros aplicados. Intente ampliar los parámetros en el panel izquierdo.")
    st.stop()

# --- FILA 1: KPIs (Micro-tarjetas Bento) ---

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    with st.container(border=True):
        st.markdown(
            f"""
            <div class='kpi-title'>📚 Publicaciones Analizadas</div>
            <div class='kpi-value'>{len(df_filtered)}</div>
            """,
            unsafe_allow_html=True
        )

with kpi2:
    with st.container(border=True):
        st.markdown(
            f"""
            <div class='kpi-title'>🎯 Citaciones Totales</div>
            <div class='kpi-value'>{df_filtered['Cited by'].sum()}</div>
            """,
            unsafe_allow_html=True
        )

with kpi3:
    with st.container(border=True):
        avg_cit = df_filtered['Cited by'].mean()
        st.markdown(
            f"""
            <div class='kpi-title'>📈 Promedio de Citaciones por Artículo</div>
            <div class='kpi-value'>{avg_cit:.1f}</div>
            """,
            unsafe_allow_html=True
        )
with kpi4:
    with st.container(border=True):
        oa_pct = (df_filtered['Access_Type'] == 'Open Access').sum() / len(df_filtered) * 100
        st.markdown(
            f"""
            <div class='kpi-title'>🌐 Acceso Abierto</div>
            <div class='kpi-value kpi-highlight'>{oa_pct:.1f}%</div>
            """,
            unsafe_allow_html=True
        )
st.write("")

st.caption(
    "Indicadores generales de producción científica, impacto académico y disponibilidad de acceso en la literatura analizada."
)
# FILA 2: EVOLUCIÓN Y LÍNEAS DE INVESTIGACIÓN

col_left, col_right = st.columns([6,4])

with col_left:
    with st.container(border=True):

        st.subheader("📈 Evolución de las Publicaciones Científicas")

        st.caption(
            "Crecimiento de la producción científica sobre inteligencia artificial y aprendizaje automático en salud materna e infantil."
        )

        df_yearly = (
            df_filtered
            .groupby("Year")
            .size()
            .reset_index(name="Documentos")
        )

        fig_line = px.line(
            df_yearly,
            x="Year",
            y="Documentos",
            markers=True,
            template="plotly_dark",
            color_discrete_sequence=["#06b6d4"]
        )

        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=380
        )

        st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    with st.container(border=True):

        st.subheader("🔍 Principales Líneas de Investigación")

        st.caption(
            "Temáticas más frecuentes identificadas en los títulos de las publicaciones."
        )

        all_titles = " ".join(
            df_filtered["Title"].str.lower().tolist()
        )

        words = re.findall(r"\b[a-z]{4,}\b", all_titles)

        stop_words = {
            "with","from","using","study","analysis",
            "based","health","maternal","child",
            "pregnant","women","model","learning",
            "machine","artificial","intelligence"
        }

        filtered_words = [
            w for w in words
            if w not in stop_words
        ]

        word_counts = Counter(filtered_words).most_common(10)

        df_words = pd.DataFrame(
            word_counts,
            columns=["Término","Frecuencia"]
        )

        fig_words = px.bar(
            df_words,
            x="Frecuencia",
            y="Término",
            orientation="h",
            template="plotly_dark",
            color_discrete_sequence=["#8b5cf6"]
        )

        fig_words.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=380,
            yaxis={"categoryorder":"total ascending"}
        )

        st.plotly_chart(fig_words, use_container_width=True)


# FILA 3: REVISTAS Y ARTÍCULOS MÁS CITADOS

col_journal, col_cited = st.columns(2)

with col_journal:
    with st.container(border=True):

        st.subheader("📚 Revistas con Mayor Producción Científica")

        st.caption(
            "Fuentes que concentran la mayor cantidad de investigaciones del área."
        )

        top_journals = (
            df_filtered["Source title"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        top_journals.columns = [
            "Revista",
            "Publicaciones"
        ]

        fig_journal = px.bar(
            top_journals,
            x="Publicaciones",
            y="Revista",
            orientation="h",
            template="plotly_dark",
            color="Publicaciones",
            color_continuous_scale="Teal"
        )

        fig_journal.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=430,
            coloraxis_showscale=False,
            yaxis={"categoryorder":"total ascending"}
        )

        st.plotly_chart(fig_journal, use_container_width=True)

with col_cited:
    with st.container(border=True):

        st.subheader("🏆 Artículos con Mayor Impacto Científico")

        st.caption(
            "Publicaciones que han recibido más citaciones dentro del conjunto analizado."
        )

        df_top = (
            df_filtered
            .nlargest(10, "Cited by")
            .copy()
        )

        df_top["Título Corto"] = (
            df_top["Title"]
            .apply(
                lambda x:
                x[:50] + "..."
                if len(x) > 50
                else x
            )
        )

        fig_bar = px.bar(
            df_top,
            x="Cited by",
            y="Título Corto",
            orientation="h",
            template="plotly_dark",
            color="Cited by",
            color_continuous_scale="Teal"
        )

        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=430,
            coloraxis_showscale=False,
            yaxis={"categoryorder":"total ascending"}
        )

        st.plotly_chart(fig_bar, use_container_width=True)

col_oa, col_doc = st.columns(2)

with col_oa:
    with st.container(border=True):

        st.subheader("🔓 Disponibilidad del Conocimiento")
        st.caption("Distribución de publicaciones según acceso abierto.")

        oa = (
            df_filtered["Access_Type"]
            .fillna("Desconocido")
            .value_counts()
            .reset_index()
        )

        oa.columns = ["Tipo", "Cantidad"]

        fig_oa = px.pie(
            oa,
            names="Tipo",
            values="Cantidad",
            hole=0.65,
            template="plotly_dark",
            color_discrete_sequence=[
                "#00D4FF",  # azul eléctrico
                "#7C4DFF",  # morado
                "#00E676",  # verde neón
                "#00B0FF"   # azul profundo
            ]
        )

        fig_oa.update_traces(
            textinfo="percent+label",
            pull=[0.03] * len(oa)
        )

        fig_oa.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=380,
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True
        )

        st.plotly_chart(fig_oa, use_container_width=True)
with col_doc:
    with st.container(border=True):

        st.subheader("📄 Tipología de la Producción Científica")
        st.caption("Diversidad de tipos de documentos en la literatura científica.")

        doc = (
            df_filtered["Document Type"]
            .fillna("Desconocido")
            .value_counts()
            .head(8)
            .reset_index()
        )

        doc.columns = ["Tipo", "Cantidad"]

        doc["Cantidad"] = pd.to_numeric(doc["Cantidad"], errors="coerce")
        doc = doc.dropna()

        fig_doc = px.pie(
            doc,
            names="Tipo",
            values="Cantidad",
            hole=0.55,
            template="plotly_dark",
            color_discrete_sequence=[
                "#FF3D00",  # rojo intenso
                "#FF6D00",  # naranja
                "#FFEA00",  # amarillo
                "#FF1744",  # rojo rosado
                "#D500F9",  # fucsia
                "#651FFF",  # violeta
                "#00E5FF",  # cyan
                "#FF4081"   # rosa fuerte
            ]
        )

        fig_doc.update_traces(
            textinfo="percent+label",
            pull=[0.04] * len(doc),
            rotation=90
        )

        fig_doc.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=520,  # 🔥 MÁS GRANDE
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend_title_text="Tipo de documento"
        )

        st.plotly_chart(fig_doc, use_container_width=True)    
# ==============================================================================
# 📂 REPOSITORIO + DESCARGA CSV (SIN ERRORES)
# ==============================================================================
with st.container(border=True):

    st.subheader("📂 Repositorio de Evidencia")
    st.caption("Detalle de los documentos según los filtros aplicados. Puede exportar estos datos.")

    # columnas seguras (evita crash si falta alguna)
    base_cols = ['Authors', 'Title', 'Year', 'Source title', 'Cited by']
    safe_cols = [c for c in base_cols if c in df_filtered.columns]

    st.dataframe(
        df_filtered[safe_cols],
        use_container_width=True,
        height=330
    )

    # export CSV
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Exportar Vista Actual a CSV",
        data=csv_data,
        file_name="scopus_salud_materno_infantil.csv",
        mime="text/csv",
        help="Descarga los datos filtrados para Excel o Python."
    )
        
