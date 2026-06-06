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
st.title("Inteligencia Artificial en la Salud Materno-Infantil")

# Bloque de Empatía con el Usuario (Contexto y Guía)
st.markdown("""
<div class="user-guide">
    <strong>Propósito del Dashboard:</strong> Este entorno interactivo responde a la pregunta de investigación sobre las aplicaciones del Machine Learning en la salud materna e infantil. 
    Explore la evolución temporal, identifique los artículos más influyentes y descubra los enfoques metodológicos más frecuentes en la literatura extraída de Scopus.
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("⚠️ No hay documentos que coincidan con los filtros aplicados. Intente ampliar los parámetros en el panel izquierdo.")
    st.stop()

# --- FILA 1: KPIs (Micro-tarjetas Bento) ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    with st.container(border=True):
        st.markdown(f"<div class='kpi-title'>Total de Estudios</div><div class='kpi-value'>{len(df_filtered)}</div>", unsafe_allow_html=True)
with kpi2:
    with st.container(border=True):
        st.markdown(f"<div class='kpi-title'>Impacto Acumulado</div><div class='kpi-value'>{df_filtered['Cited by'].sum()}</div>", unsafe_allow_html=True)
with kpi3:
    with st.container(border=True):
        avg_cit = df_filtered['Cited by'].mean()
        st.markdown(f"<div class='kpi-title'>Promedio Citas</div><div class='kpi-value'>{avg_cit:.1f}</div>", unsafe_allow_html=True)
with kpi4:
    with st.container(border=True):
        oa_pct = (df_filtered['Access_Type'] == 'Open Access').sum() / len(df_filtered) * 100
        st.markdown(f"<div class='kpi-title'>Tasa Open Access</div><div class='kpi-value kpi-highlight'>{oa_pct:.1f}%</div>", unsafe_allow_html=True)

st.write("") # Espaciador

# --- FILA 2: BENTO GRID PRINCIPAL (Gráficos asimétricos) ---
# Usamos proporciones 60% / 40% para romper la simetría y darle aspecto de dashboard moderno
col_left, col_right = st.columns([6, 4])

with col_left:
    with st.container(border=True):
        st.subheader("📈 Evolución de la Producción Científica")
        st.caption("Visualiza cómo ha crecido el interés en la aplicación de IA en este campo a lo largo de los años.")
        df_yearly = df_filtered.groupby('Year').size().reset_index(name='Documentos')
        fig_line = px.line(df_yearly, x='Year', y='Documentos', markers=True, template='plotly_dark', color_discrete_sequence=['#06b6d4'])
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0), height=350)
        st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    with st.container(border=True):
        st.subheader("🔍 Enfoques Principales (Keywords)")
        st.caption("Términos más recurrentes en los títulos, indicando las subáreas de mayor estudio.")
        
        all_titles = " ".join(df_filtered['Title'].str.lower().tolist())
        words = re.findall(r'\b[a-z]{4,}\b', all_titles)
        stop_words = {'with', 'from', 'using', 'study', 'analysis', 'based', 'health', 'maternal', 'child', 'pregnant', 'women', 'model', 'learning', 'machine', 'artificial', 'intelligence'}
        filtered_words = [w for w in words if w not in stop_words]
        
        word_counts = Counter(filtered_words).most_common(10)
        df_words = pd.DataFrame(word_counts, columns=['Término', 'Frecuencia'])
        
        fig_words = px.bar(df_words, x='Frecuencia', y='Término', orientation='h', template='plotly_dark', color_discrete_sequence=['#8b5cf6'])
        fig_words.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder': 'total ascending'}, margin=dict(l=0, r=0, t=30, b=0), height=350)
        st.plotly_chart(fig_words, use_container_width=True)

# --- FILA 3: BENTO GRID SECUNDARIO (Impacto y Datos crudos) ---
col_bottom_left, col_bottom_right = st.columns([5, 5])

with col_bottom_left:
    with st.container(border=True):
        st.subheader("🏆 Literatura Fundamental")
        st.caption("Los 10 artículos con mayor cantidad de citas (indicador de autoridad en la materia).")
        df_top = df_filtered.nlargest(10, 'Cited by').copy()
        df_top['Título Corto'] = df_top['Title'].apply(lambda x: x[:50] + "..." if len(x) > 50 else x)
        
        fig_bar = px.bar(df_top, x='Cited by', y='Título Corto', orientation='h', template='plotly_dark', color='Cited by', color_continuous_scale='Teal')
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder': 'total ascending'}, margin=dict(l=0, r=0, t=30, b=0), height=400, coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

with col_bottom_right:
    with st.container(border=True):
        st.subheader("📂 Repositorio de Evidencia")
        st.caption("Detalle de los documentos según los filtros aplicados. Puede exportar estos datos.")
        display_cols = ['Authors', 'Title', 'Year', 'Source title', 'Cited by']
        st.dataframe(df_filtered[display_cols], use_container_width=True, height=330)
        
        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar Vista Actual a CSV",
            data=csv_data,
            file_name="scopus_salud_materno_infantil.csv",
            mime="text/csv",
            help="Descarga los datos filtrados para un análisis externo en Excel o Python."
        )