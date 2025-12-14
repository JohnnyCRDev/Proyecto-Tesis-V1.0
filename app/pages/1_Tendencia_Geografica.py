import streamlit as st
import pandas as pd
import pydeck as pdk

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
    page_title="Dashboard INEN - Tendencias Geográficas",
    page_icon="",
    layout="wide"
)

st.title("ANÁLISIS DE LAS TENDENCIAS GEOGRÁFICAS DE LOS EGRESOS HOSPITALARIOS")
st.markdown("""
<div style='text-align: justify; font-size:16px; color:#ffff; line-height:1.6;'>
Visualiza la distribución geográfica de los <b>egresos hospitalarios</b> según 
<b>departamento, provincia y distrito</b>.
</div>
<hr style='margin-top:10px;'>
""", unsafe_allow_html=True)

# ========================
# CARGA DE DATOS
# ========================
@st.cache_data
def cargar_datos():
    ruta = "data/listado_limpio.csv"   # tu dataset principal local
    df = pd.read_csv(ruta, encoding='latin1')
    for col in ["DEPARTAMENTO", "PROVINCIA", "DISTRITO"]:
        df[col] = df[col].astype(str).str.strip().str.upper()
    return df

@st.cache_data
def cargar_coordenadas():
    # Enlace de Google Drive transformado a formato descargable
    ruta_coords = "https://drive.google.com/uc?id=1kDZOXpLUIGijelqasAmm-OgB1lrPmnAW"
    df_coords = pd.read_csv(ruta_coords, encoding="utf-8-sig")
    for col in ["DEPARTAMENTO", "PROVINCIA", "DISTRITO"]:
        df_coords[col] = df_coords[col].astype(str).str.strip().str.upper()
    return df_coords

df = cargar_datos()
df_coords = cargar_coordenadas()

# ========================
# FILTROS GEOGRÁFICOS
# ========================
st.sidebar.header("Filtros Geográficos")

departamentos = sorted(df["DEPARTAMENTO"].dropna().unique())
dpto_sel = st.sidebar.selectbox("Selecciona Departamento:", ["(Todos)"] + departamentos)

if dpto_sel != "(Todos)":
    provincias = sorted(df[df["DEPARTAMENTO"] == dpto_sel]["PROVINCIA"].dropna().unique())
else:
    provincias = sorted(df["PROVINCIA"].dropna().unique())

prov_sel = st.sidebar.selectbox("Selecciona Provincia:", ["(Todas)"] + provincias)

if prov_sel != "(Todas)":
    distritos = sorted(df[df["PROVINCIA"] == prov_sel]["DISTRITO"].dropna().unique())
else:
    if dpto_sel != "(Todos)":
        distritos = sorted(df[df["DEPARTAMENTO"] == dpto_sel]["DISTRITO"].dropna().unique())
    else:
        distritos = sorted(df["DISTRITO"].dropna().unique())

dist_sel = st.sidebar.selectbox("Selecciona Distrito:", ["(Todos)"] + distritos)

# ========================
# APLICAR FILTROS
# ========================
df_filtrado = df.copy()
if dpto_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["DEPARTAMENTO"] == dpto_sel]
if prov_sel != "(Todas)":
    df_filtrado = df_filtrado[df_filtrado["PROVINCIA"] == prov_sel]
if dist_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["DISTRITO"] == dist_sel]

# ========================
# CALCULAR EGRESOS POR DISTRITO
# ========================
egresos_por_distrito = df_filtrado.groupby(
    ["DEPARTAMENTO", "PROVINCIA", "DISTRITO"]
).size().reset_index(name="EGRESOS")

# ========================
# UNIR CON COORDENADAS
# ========================
df_mapa = pd.merge(
    egresos_por_distrito,
    df_coords,
    on=["DEPARTAMENTO", "PROVINCIA", "DISTRITO"],
    how="left"
).dropna(subset=["LATITUD", "LONGITUD"])

# ========================
# MAPA
# ========================
st.subheader("Mapa Geográfico de Egresos Hospitalarios")

if df_mapa.empty:
    st.warning("No hay coordenadas disponibles para los filtros seleccionados.")
else:
    df_mapa = df_mapa.rename(columns={"LATITUD": "lat", "LONGITUD": "lon"})

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_mapa,
        get_position="[lon, lat]",
        get_color="[0, 128, 255, 180]",
        get_radius=2900,
        pickable=True,
        opacity=0.8,
    )

    view_state = pdk.ViewState(
        latitude=df_mapa["lat"].mean(),
        longitude=df_mapa["lon"].mean(),
        zoom=5,
        pitch=0,
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "Departamento: {DEPARTAMENTO}\nProvincia: {PROVINCIA}\nDistrito: {DISTRITO}"}
        ),
        use_container_width=True,
        height=800
    )