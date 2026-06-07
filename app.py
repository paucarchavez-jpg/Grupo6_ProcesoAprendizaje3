import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import re

st.set_page_config(
    page_title="IA en Salud Materna e Infantil",
    layout="wide"
)

@st.cache_data
def load_data():
    return pd.read_csv("scopus_PA3.csv")

df = load_data()

df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Cited by"] = pd.to_numeric(df["Cited by"], errors="coerce").fillna(0)

APPLICATIONS = {
    "Prediction":["prediction","predicting","predictive","predict"],
    "Diagnosis":["diagnosis","diagnostic","detect","detection"],
    "Risk Assessment":["risk"],
    "Screening":["screening"],
    "Classification":["classifier","classification"],
    "Monitoring":["monitoring"],
    "Chatbot":["chatbot"],
    "Decision Support":["decision"]
}

def detect_application(title):
    title = str(title).lower()
    for app, words in APPLICATIONS.items():
        for w in words:
            if w in title:
                return app
    return "Other"

HEALTH_AREAS = {
    "Maternal Health":["maternal","pregnancy","pregnant","obstetric"],
    "Child Health":["child","children","pediatric"],
    "Neonatal Health":["neonatal","newborn","infant"]
}

def detect_area(title):
    title = str(title).lower()
    for area, words in HEALTH_AREAS.items():
        for w in words:
            if w in title:
                return area
    return "Other"

df["Application"] = df["Title"].apply(detect_application)
df["Health Area"] = df["Title"].apply(detect_area)

st.title("🤖 IA y Machine Learning en Salud Materna e Infantil")

st.markdown("""
### Pregunta de investigación
**¿Cuáles son las aplicaciones de la inteligencia artificial y el aprendizaje automático en la salud materna e infantil?**
""")

st.sidebar.header("Filtros")

years = st.sidebar.slider(
    "Años",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (int(df["Year"].min()), int(df["Year"].max()))
)

df_filtered = df[
    (df["Year"] >= years[0]) &
    (df["Year"] <= years[1])
]

k1,k2,k3,k4 = st.columns(4)

with k1:
    st.metric("Artículos", len(df_filtered))

with k2:
    st.metric("Citas Totales", int(df_filtered["Cited by"].sum()))

with k3:
    st.metric("Promedio Citas", round(df_filtered["Cited by"].mean(),1))

with k4:
    oa = df_filtered["Open Access"].notna().mean()*100
    st.metric("% Open Access", f"{oa:.1f}%")

st.divider()

c1,c2 = st.columns(2)

with c1:
    yearly = df_filtered.groupby("Year").size().reset_index(name="Publicaciones")

    fig = px.bar(
        yearly,
        x="Year",
        y="Publicaciones",
        title="Evolución de las Publicaciones Científicas",
        color="Publicaciones",
        color_continuous_scale=["#d1ab71","#bbcdc5","#8ea19b"]
    )

    st.plotly_chart(fig, use_container_width=True)

with c2:
    apps = df_filtered["Application"].value_counts().reset_index()
    apps.columns=["Aplicación","Cantidad"]

    fig = px.bar(
        apps,
        x="Cantidad",
        y="Aplicación",
        orientation="h",
        title="Aplicaciones de IA identificadas",
        color="Cantidad",
        color_continuous_scale=["#d1ab71","#bbcdc5","#8ea19b"]
    )

    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(fig, use_container_width=True)

c3,c4 = st.columns(2)

with c3:
    journals = (
        df_filtered["Source title"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    journals.columns=["Revista","Cantidad"]

    fig = px.bar(
        journals,
        x="Cantidad",
        y="Revista",
        orientation="h",
        title="Top 10 Revistas",
        color="Cantidad",
        color_continuous_scale=["#d1ab71","#bbcdc5","#8ea19b"]
    )

    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(fig, use_container_width=True)

with c4:
    docs = (
        df_filtered["Document Type"]
        .value_counts()
        .reset_index()
    )

    docs.columns=["Tipo","Cantidad"]

    fig = px.pie(
        docs,
        values="Cantidad",
        names="Tipo",
        hole=0.55,
        title="Tipo de Documento"
    )

    st.plotly_chart(fig, use_container_width=True)

c5,c6 = st.columns(2)

with c5:
    top = (
        df_filtered
        .sort_values("Cited by", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top,
        x="Cited by",
        y="Title",
        orientation="h",
        title="Top 10 Artículos más Citados",
        color="Cited by",
        color_continuous_scale=["#d1ab71","#bbcdc5","#8ea19b"]
    )

    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(fig, use_container_width=True)

with c6:
    area = (
        df_filtered["Health Area"]
        .value_counts()
        .reset_index()
    )

    area.columns=["Área","Cantidad"]

    fig = px.treemap(
        area,
        path=["Área"],
        values="Cantidad",
        title="Áreas de Salud Investigadas"
    )

    st.plotly_chart(fig, use_container_width=True)

st.subheader("Conclusiones automáticas")

top_app = df_filtered["Application"].value_counts().idxmax()
top_area = df_filtered["Health Area"].value_counts().idxmax()

st.success(
f"""
• Aplicación más estudiada: {top_app}

• Área más investigada: {top_area}

• Total de artículos analizados: {len(df_filtered)}

• La literatura muestra un fuerte uso de IA y Machine Learning para predicción, diagnóstico y evaluación de riesgos en salud materna e infantil.
"""
)

st.subheader("Base de datos")

st.dataframe(
    df_filtered[["Title","Year","Source title","Cited by"]],
    use_container_width=True
)
