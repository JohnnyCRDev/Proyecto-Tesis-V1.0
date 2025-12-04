import streamlit as st
import pandas as pd
import math

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

# TÍTULO Y DESCRIPCIÓN

st.set_page_config(
    page_title="Dashboard INEN - Egresos Hospitalarios",
    page_icon="",
    layout="wide"
)

# ========================
# TÍTULO PERSONALIZADO (con HTML)
# ========================
st.markdown("""
<style>
.titulo-principal {
    font-size: 40px;              /* Tamaño del texto */
    color: #0d6efd;               /* Color azul tipo institucional */
    text-align: center;           /* Centrar el texto */
    font-weight: 700;             /* Negrita */
    font-family: 'Segoe UI', sans-serif; /* Fuente moderna */
    margin-bottom: 10px;          /* Espacio inferior */
}
.subtitulo {
    font-size: 18px;
    text-align: center;
    color: #0d6efd;
    font-family: 'Segoe UI', sans-serif;
}
.linea {
    border-top: 3px solid #0d6efd;
    width: 70%;
    margin: 0 auto 30px auto;     /* Centrar la línea */
}
</style>
""", unsafe_allow_html=True)

# Título y subtítulo
st.markdown('<h1 class="titulo-principal"> DASHBOARD INTERACTIVO - EGRESOS HOSPITALARIOS INEN (2022–2025)</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Sistema Interactivo de Análisis de Tendencias Geográficas, Demográficas y Temporales con datos abiertas obtenidos del portal de datos abiertos del INEN</p>', unsafe_allow_html=True)
#st.markdown('<div class="linea"></div>', unsafe_allow_html=True)


# CARGA DE DATOS
@st.cache_data
def cargar_datos():
    ruta = r"D:\\PROGRAMA DE TESIS 2025 - PREGRADO\\DATASET EGRESOS HOSPITALARIOS INEN\\Proyecto Tesis V1.0\\data\\listado_limpio.csv"
    df = pd.read_csv(ruta, encoding='latin1')
    return df

with st.spinner("Cargando datos, por favor espera..."):
    df = cargar_datos()

#st.success(f"✅ Datos cargados correctamente: {df.shape[0]:,} registros y {df.shape[1]} columnas.")

# INFORMACIÓN FINAL
st.caption("Usa el buscador para filtrar registros y cambia la página para navegar por los resultados.")

# MOSTRAR RESULTADOS
st.subheader("DATOS GENERALES")
st.write(f"**Total de registros:** {len(df):,}")

columnas_a_mostrar = [
    "NUMERO", "SEXO", "EDAD", "FECHA_INGRESO", "FECHA_EGRESO",
    "DEPARTAMENTO", "PROVINCIA", "DISTRITO"
]

# Verificar que existan en el dataset
columnas_a_mostrar = [col for col in columnas_a_mostrar if col in df.columns]
df = df[columnas_a_mostrar]

# FILTRO DE BÚSQUEDA + PAGINACIÓN (en una fila)

# Crear dos columnas (60% - 40%)
col1, col2 = st.columns([3, 1.5])

with col1:
    busqueda = st.text_input("Buscar en la tabla (por palabra clave):")

if busqueda:
    df_filtrado = df[df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False, na=False).any(), axis=1)]
else:
    df_filtrado = df

# Paginación
filas_por_pagina = 50
total_filas = len(df_filtrado)
total_paginas = math.ceil(total_filas / filas_por_pagina)

with col2:
    pagina = st.number_input(
        "Página:",
        min_value=1,
        max_value=max(total_paginas, 1),
        value=1,
        step=1,
        key="pagina_selector"
    )

inicio = (pagina - 1) * filas_por_pagina
fin = inicio + filas_por_pagina

# ========================
# MOSTRAR TABLA
# ========================
st.write(f"Mostrando registros {inicio+1} - {min(fin, total_filas)} de {total_filas:,}")
st.dataframe(df_filtrado.iloc[inicio:fin])