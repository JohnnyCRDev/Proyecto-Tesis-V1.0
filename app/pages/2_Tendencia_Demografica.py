import streamlit as st
import pandas as pd
import plotly.express as px

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

# ========================
# CONFIGURACIÓN INICIAL
# ========================
st.set_page_config(
    page_title="Dashboard INEN - Egresos Hospitalarios",
    page_icon="",
    layout="wide"
)

st.title("Gráficos de Tendencias Demográficas")

# ========================
# CARGA DE DATOS
# ========================
@st.cache_data
def cargar_datos():
    ruta = r"D:\PROGRAMA DE TESIS 2025 - PREGRADO\DATASET EGRESOS HOSPITALARIOS INEN\Proyecto Tesis V1.0\data\listado_limpio.csv"
    df = pd.read_csv(ruta, encoding='utf-8-sig')
    return df

df = cargar_datos()
st.success(f"Datos cargados correctamente: {df.shape[0]} registros listos para análisis.")

# ========================
# NORMALIZAR CAMPOS
# ========================
for col in ['DEPARTAMENTO', 'PROVINCIA', 'DISTRITO', 'SEXO']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.upper()

# Crear rangos de edad
if 'EDAD' in df.columns:
    df['RANGO_EDAD'] = pd.cut(
        df['EDAD'],
        bins=[0, 12, 18, 30, 45, 60, 75, 200],
        labels=['0-12', '13-18', '19-30', '31-45', '46-60', '61-75', '75+'],
        right=True
    )

# ========================
# FILTROS GEOGRÁFICOS
# ========================
st.sidebar.header("Filtros Geográficos")

departamentos = sorted(df['DEPARTAMENTO'].dropna().unique())
dpto_sel = st.sidebar.selectbox("Selecciona Departamento:", ["(Todos)"] + list(departamentos))

df_f = df.copy()

if dpto_sel != "(Todos)":
    df_f = df_f[df_f['DEPARTAMENTO'] == dpto_sel]

provincias = sorted(df_f['PROVINCIA'].dropna().unique())
prov_sel = st.sidebar.selectbox("Selecciona Provincia:", ["(Todas)"] + list(provincias))

if prov_sel != "(Todas)":
    df_f = df_f[df_f['PROVINCIA'] == prov_sel]

distritos = sorted(df_f['DISTRITO'].dropna().unique())
dist_sel = st.sidebar.selectbox("Selecciona Distrito:", ["(Todos)"] + list(distritos))

if dist_sel != "(Todos)":
    df_f = df_f[df_f['DISTRITO'] == dist_sel]

# ========================
# FILTROS DE AÑO
# ========================
st.sidebar.header("Filtros de Año")

anios_ingreso = sorted(df_f['ANIO_EGRESO'].dropna().unique())
anio_ing_sel = st.sidebar.selectbox("Año de Egreso:", ["(Todos)"] + list(map(int, anios_ingreso)))

if anio_ing_sel != "(Todos)":
    df_f = df_f[df_f['ANIO_EGRESO'] == int(anio_ing_sel)]

# ========================
# GRÁFICOS
# ========================

st.subheader("Resultados filtrados")
st.info(f"Registros después de filtros: **{len(df_f):,}**")

# ========================
# GRÁFICO 1: EGRESOS POR SEXO
# ========================
st.subheader("Egresos por Sexo")

if 'SEXO' in df_f.columns:
    df_sexo = df_f.groupby('SEXO').size().reset_index(name='TOTAL')

    fig1 = px.bar(
        df_sexo,
        x='SEXO',
        y='TOTAL',
        text='TOTAL',
        title="Distribución de Egresos por Sexo",
        labels={'TOTAL': 'Cantidad de Egresos'},
    )

    st.plotly_chart(fig1, use_container_width=True)
    st.write(f"**Total general mostrado: {df_sexo['TOTAL'].sum():,} egresos**")
else:
    st.warning("No existe columna SEXO en el dataset.")

# ========================
# GRÁFICO 2: EGRESOS POR RANGO DE EDAD
# ========================
st.subheader("Egresos por Rango de Edad")

if 'RANGO_EDAD' in df_f.columns:
    df_edad = df_f.groupby('RANGO_EDAD').size().reset_index(name='TOTAL')

    fig2 = px.bar(
        df_edad,
        x='RANGO_EDAD',
        y='TOTAL',
        text='TOTAL',
        title="Cantidad de Egresos por Rango de Edad",
        labels={'RANGO_EDAD': 'Rango de Edad', 'TOTAL': 'Cantidad'}
    )

    st.plotly_chart(fig2, use_container_width=True)
    st.write(f"**Total general mostrado: {df_edad['TOTAL'].sum():,} egresos**")
else:
    st.warning("No existe columna EDAD o no pudo generarse el rango.")

# ========================
# FIN
# ========================
st.success("✔️ Módulo de análisis ejecutado correctamente.")