import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import numpy as np

st.markdown("""
<style>
    .stApp {
        background-color: #123673;
    }
    [data-testid="stSidebar"] {
        background-color: #123673;
    }
    [data-testid="stSidebar"] * {
        color: #ffff !important;
    }
</style>
""", unsafe_allow_html=True)

# =======================================
# CONFIGURACIÓN INICIAL
# =======================================
st.set_page_config(
    page_title="Dashboard INEN - Tendencias Geográficas",
    page_icon="",
    layout="wide"
)

st.title("ANÁLISIS DE LAS TENDENCIAS GEOGRÁFICAS DE LOS EGRESOS HOSPITALARIOS")

st.markdown("""
<div style='text-align: justify; font-size:16px; line-height:1.6;'>
Este módulo permite analizar la distribución geográfica de los <b>egresos hospitalarios</b> 
según <b>departamento, provincia y distrito</b>, incluyendo tendencias, estadísticas descriptivas 
y correlaciones exploratorias.
</div>
<hr>
""", unsafe_allow_html=True)

# =======================================
# CARGA DE DATOS DESDE GOOGLE DRIVE
# =======================================
@st.cache_data
def cargar_datos():
    url = "https://drive.google.com/uc?id=18e0Hi6sOm9yfOJKP9LaS8cm2MHzz_Lry"
    df = pd.read_csv(url, encoding='utf-8-sig')
    return df

df = cargar_datos()

st.success(f"Datos cargados correctamente: **{df.shape[0]} registros totales**")

# =======================================
# FUNCIONES AUXILIARES (SPEARMAN MANUAL)
# =======================================
def rank_values(series):
    temp = pd.DataFrame({"v": series})
    temp["rank"] = temp["v"].rank(method="average")
    return temp["rank"].values

def spearman_manual(x, y):
    x = pd.to_numeric(x, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")
    df_valid = pd.DataFrame({"x": x, "y": y}).dropna()

    if len(df_valid) < 3: 
        return None
    if df_valid["x"].nunique() < 2 or df_valid["y"].nunique() < 2:
        return None

    rx = rank_values(df_valid["x"])
    ry = rank_values(df_valid["y"])

    return np.corrcoef(rx, ry)[0, 1]

# =======================================
# FILTROS
# =======================================
st.sidebar.header("Filtros")

# ===== Filtro Año de Egreso =====
años_min_e = int(df["ANIO_EGRESO"].min())
años_max_e = int(df["ANIO_EGRESO"].max())

rango_años_egreso = st.sidebar.slider(
    "Filtrar por Año de Egreso:",
    min_value=años_min_e,
    max_value=años_max_e,
    value=(años_min_e, años_max_e)
)

df = df[(df["ANIO_EGRESO"] >= rango_años_egreso[0]) & 
        (df["ANIO_EGRESO"] <= rango_años_egreso[1])]

# ===== NUEVO → Filtro Año de Ingreso =====
años_min_i = int(df["ANIO_INGRESO"].min())
años_max_i = int(df["ANIO_INGRESO"].max())

rango_años_ingreso = st.sidebar.slider(
    "Filtrar por Año de Ingreso:",
    min_value=años_min_i,
    max_value=años_max_i,
    value=(años_min_i, años_max_i)
)

df = df[(df["ANIO_INGRESO"] >= rango_años_ingreso[0]) &
        (df["ANIO_INGRESO"] <= rango_años_ingreso[1])]

# ===== Filtros Geográficos =====
for col in ['DEPARTAMENTO', 'PROVINCIA', 'DISTRITO']:
    df[col] = df[col].astype(str).str.strip().str.upper()

departamentos = sorted(df['DEPARTAMENTO'].dropna().unique())
dpto_sel = st.sidebar.selectbox("Selecciona Departamento:", ["(Todos)"] + list(departamentos))

if dpto_sel != "(Todos)":
    provincias = sorted(df[df['DEPARTAMENTO'] == dpto_sel]['PROVINCIA'].dropna().unique())
else:
    provincias = sorted(df['PROVINCIA'].dropna().unique())

prov_sel = st.sidebar.selectbox("Selecciona Provincia:", ["(Todas)"] + list(provincias))

if prov_sel != "(Todas)":
    distritos = sorted(df[df['PROVINCIA'] == prov_sel]['DISTRITO'].dropna().unique())
else:
    if dpto_sel != "(Todos)":
        distritos = sorted(df[df['DEPARTAMENTO'] == dpto_sel]['DISTRITO'].dropna().unique())
    else:
        distritos = sorted(df['DISTRITO'].dropna().unique())

dist_sel = st.sidebar.selectbox("Selecciona Distrito:", ["(Todos)"] + list(distritos))

# Aplicar filtros finales
df_filtrado = df.copy()
if dpto_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado['DEPARTAMENTO'] == dpto_sel]
if prov_sel != "(Todas)":
    df_filtrado = df_filtrado[df_filtrado['PROVINCIA'] == prov_sel]
if dist_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado['DISTRITO'] == dist_sel]

st.info(f"Registros filtrados: **{df_filtrado.shape[0]}**")

# =======================================
# ESTADÍSTICAS DESCRIPTIVAS
# =======================================
st.subheader("Estadísticas Descriptivas")

conteo_departamento_egreso = df_filtrado["DEPARTAMENTO"].value_counts(normalize=True) * 100
porcentaje_lima_egreso = conteo_departamento_egreso.get("LIMA", 0)
porcentaje_otros_egreso = 100 - porcentaje_lima_egreso

conteo_ingreso = df_filtrado["DEPARTAMENTO"].value_counts(normalize=True) * 100
porcentaje_lima_ingreso = conteo_ingreso.get("LIMA", 0)
porcentaje_otros_ingreso = 100 - porcentaje_lima_ingreso

colA, colB, colC, colD = st.columns(4)

with colA:
    st.metric("% de egresos en Lima", f"{porcentaje_lima_egreso:.1f}%")

with colB:
    st.metric("% de egresos en otras regiones", f"{porcentaje_otros_egreso:.1f}%")

with colC:
    st.metric("% de ingresos en Lima", f"{porcentaje_lima_ingreso:.1f}%")

with colD:
    st.metric("% de ingresos en otras regiones", f"{porcentaje_otros_ingreso:.1f}%")

# =======================================
# SPEARMAN GEOGRÁFICO
# =======================================
st.subheader("Correlación Exploratoria (Spearman)")

grupos = df_filtrado.groupby("LUGAR_RESIDENCIA").size().reset_index(name="Egresos")

grupos["rank_loc"] = grupos["LUGAR_RESIDENCIA"].rank(method="dense")
grupos["rank_num"] = grupos["Egresos"].rank(method="average")

spearman_geo = spearman_manual(grupos["rank_loc"], grupos["rank_num"])

if spearman_geo is None:
    st.warning("No es posible calcular Spearman con los datos filtrados.")
else:
    st.success(f"Coeficiente de Spearman: **{spearman_geo:.3f}**")

# =======================================
# VISUALIZACIONES
# =======================================
st.subheader("Visualizaciones Geográficas")

col1, col2 = st.columns([1, 1])

with col1:
    fig1 = px.bar(
        df_filtrado.groupby('DEPARTAMENTO').size().reset_index(name='Egresos'),
        x='DEPARTAMENTO', y='Egresos',
        title="Egresos por Departamento", color='Egresos'
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig3 = px.pie(
        df_filtrado,
        names='DEPARTAMENTO',
        title="Distribución porcentual por Departamento"
    )
    st.plotly_chart(fig3, use_container_width=True)