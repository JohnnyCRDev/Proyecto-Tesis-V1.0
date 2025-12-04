import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ========================
# ESTILO
# ========================
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
    page_title="Tendencias Temporales - Egresos Hospitalarios",
    page_icon="",
    layout="wide"
)

st.title("Tendencias Temporales de Egresos Hospitalarios (2022-2025)")
st.write("Análisis de duración de estancia, volumen mensual y tendencias anuales basadas en datos del INEN.")

# ========================
# CARGA DE DATOS
# ========================
@st.cache_data
def cargar_datos():
    ruta = r"D:\PROGRAMA DE TESIS 2025 - PREGRADO\DATASET EGRESOS HOSPITALARIOS INEN\Proyecto Tesis V1.0\data\listado_limpio.csv"
    df = pd.read_csv(ruta, encoding='latin1', parse_dates=['FECHA_INGRESO','FECHA_EGRESO'])
    return df

df = cargar_datos()
st.success(f"Datos cargados: {df.shape[0]:,} registros.")

# ========================
# FILTROS GEOGRÁFICOS
# ========================
st.sidebar.header("Filtros Geográficos")
for col in ['DEPARTAMENTO', 'PROVINCIA', 'DISTRITO']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.upper()

departamentos = sorted(df['DEPARTAMENTO'].dropna().unique())
dpto_sel = st.sidebar.selectbox("Selecciona Departamento o Exterior:", ["(Todos)"] + departamentos)

if dpto_sel != "(Todos)":
    provincias = sorted(df[df['DEPARTAMENTO'] == dpto_sel]['PROVINCIA'].dropna().unique())
else:
    provincias = sorted(df['PROVINCIA'].dropna().unique())

prov_sel = st.sidebar.selectbox("Selecciona Provincia:", ["(Todas)"] + provincias)

if prov_sel != "(Todas)":
    distritos = sorted(df[df['PROVINCIA'] == prov_sel]['DISTRITO'].dropna().unique())
else:
    if dpto_sel != "(Todos)":
        distritos = sorted(df[df['DEPARTAMENTO'] == dpto_sel]['DISTRITO'].dropna().unique())
    else:
        distritos = sorted(df['DISTRITO'].dropna().unique())

dist_sel = st.sidebar.selectbox("Selecciona Distrito:", ["(Todos)"] + distritos)

df_filtrado = df.copy()
if dpto_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado['DEPARTAMENTO'] == dpto_sel]
if prov_sel != "(Todas)":
    df_filtrado = df_filtrado[df_filtrado['PROVINCIA'] == prov_sel]
if dist_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado['DISTRITO'] == dist_sel]

# ========================
# FILTROS DE AÑOS
# ========================
st.sidebar.header("Filtros por Rango de Años")
anio_ing_min = int(df_filtrado['FECHA_INGRESO'].dt.year.min())
anio_ing_max = int(df_filtrado['FECHA_INGRESO'].dt.year.max())
anio_egr_min = int(df_filtrado['FECHA_EGRESO'].dt.year.min())
anio_egr_max = int(df_filtrado['FECHA_EGRESO'].dt.year.max())

rango_ingreso = st.sidebar.slider(
    "Rango de años de ingreso:",
    min_value=anio_ing_min,
    max_value=anio_ing_max,
    value=(anio_ing_min, anio_ing_max)
)

rango_egreso = st.sidebar.slider(
    "Rango de años de egreso:",
    min_value=anio_egr_min,
    max_value=anio_egr_max,
    value=(anio_egr_min, anio_egr_max)
)

df_filtrado = df_filtrado[
    (df_filtrado['FECHA_INGRESO'].dt.year >= rango_ingreso[0]) &
    (df_filtrado['FECHA_INGRESO'].dt.year <= rango_ingreso[1]) &
    (df_filtrado['FECHA_EGRESO'].dt.year >= rango_egreso[0]) &
    (df_filtrado['FECHA_EGRESO'].dt.year <= rango_egreso[1])
]

st.info(f"Registros filtrados: {len(df_filtrado):,}")

# ========================
# ESTADÍSTICAS DESCRIPTIVAS
# ========================
st.subheader("Estadísticas Descriptivas")

df_filtrado['DURACION_ESTANCIA'] = (df_filtrado['FECHA_EGRESO'] - df_filtrado['FECHA_INGRESO']).dt.days
duracion_promedio = df_filtrado['DURACION_ESTANCIA'].mean()

df_filtrado['MES_EGRESO'] = df_filtrado['FECHA_EGRESO'].dt.to_period('M')
egresos_mensuales_prom = df_filtrado.groupby('MES_EGRESO').size().mean()

# Calcular egresos anuales y tendencia
df_filtrado['AÑO_EGRESO'] = df_filtrado['FECHA_EGRESO'].dt.year
egresos_anuales = df_filtrado.groupby('AÑO_EGRESO').size().reset_index(name='Egresos')
egresos_anuales['Cambio_%'] = egresos_anuales['Egresos'].pct_change() * 100
egresos_anuales['Tendencia'] = egresos_anuales['Cambio_%'].apply(
    lambda x: "Aumento" if x > 0 else ("Disminución" if x < 0 else "Sin cambio")
)

# Mostrar métricas principales
col1, col2, col3 = st.columns(3)
col1.metric("Duración promedio de estancia (días)", f"{duracion_promedio:.1f}")
col2.metric("Egresos mensuales promedio", f"{egresos_mensuales_prom:,.0f}")
col3.metric("Tendencia anual", f"{egresos_anuales['Tendencia'].iloc[-1]}")

# ========================
# TENDENCIAS TEMPORALES
# ========================
st.subheader("Tendencias Anuales y Mensuales")

def spearman_manual(x, y):
    rx = x.rank()
    ry = y.rank()
    return np.corrcoef(rx, ry)[0,1]

spearman_coef = spearman_manual(egresos_anuales['AÑO_EGRESO'], egresos_anuales['Egresos'])

fig_anual = px.line(
    egresos_anuales,
    x='AÑO_EGRESO',
    y='Egresos',
    markers=True,
    title=f"Egresos anuales (Coef. Spearman = {spearman_coef:.2f})"
)
st.plotly_chart(fig_anual, use_container_width=True)

# Egresos por mes (picos de invierno)
df_filtrado['MES_NUM'] = df_filtrado['FECHA_EGRESO'].dt.month
egresos_mensuales = df_filtrado.groupby('MES_NUM').size().reset_index(name='Egresos')
fig_mensual = px.bar(
    egresos_mensuales,
    x='MES_NUM',
    y='Egresos',
    labels={'MES_NUM':'Mes','Egresos':'Número de Egresos'},
    title="Promedio de egresos por mes"
)
st.plotly_chart(fig_mensual, use_container_width=True)

# ========================
# PATRONES POST-PANDEMIA
# ========================
st.subheader("Patrones y Recuperación Post-Pandemia")

# Convertir a string en formato YYYY-MM para evitar problemas de JSON
df_mes = df_filtrado.groupby(df_filtrado['FECHA_EGRESO'].dt.to_period('M')).size().reset_index(name='Egresos')
df_mes['MES_EGRESO'] = df_mes['FECHA_EGRESO'].astype(str)

fig_recuperacion = px.line(
    df_mes,
    x='MES_EGRESO',
    y='Egresos',
    markers=True,
    title="Serie temporal de egresos por mes"
)
st.plotly_chart(fig_recuperacion, use_container_width=True)

# ========================
# TABLA DE EGRESOS ANUALES CON TENDENCIA
# ========================
st.subheader("Egresos Anuales y Tendencia")
st.dataframe(egresos_anuales)
