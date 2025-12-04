import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

st.set_page_config(page_title="Análisis Estadístico", layout="wide")

st.title("Análisis Estadístico de Egresos Hospitalarios")

# ========================
# CARGA DE DATOS
# ========================
@st.cache_data
def load_data():
    ruta = r"D:\PROGRAMA DE TESIS 2025 - PREGRADO\DATASET EGRESOS HOSPITALARIOS INEN\Proyecto Tesis V1.0\data\listado_limpio.csv"
    df = pd.read_csv(ruta, encoding='utf-8-sig')
    return df

df = load_data()
st.success(f"Datos cargados correctamente: {df.shape[0]} registros listos para análisis.")


# ================================================================
# FILTROS (AÑO Y EDAD) – EN LA BARRA LATERAL
# ================================================================
st.sidebar.header("Filtros")

# ---- Filtro de año ----
if "ANIO_EGRESO" in df.columns:
    min_year = int(df["ANIO_EGRESO"].min())
    max_year = int(df["ANIO_EGRESO"].max())
else:
    st.error("❌ El dataset no contiene la columna 'ANIO_EGRESO'.")
    st.stop()

rango_anio = st.sidebar.slider(
    "Rango de años de egreso:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

# ---- Filtro de edad ----
min_edad = int(df["EDAD"].min())
max_edad = int(df["EDAD"].max())

rango_edad = st.sidebar.slider(
    "Rango de edad:",
    min_value=min_edad,
    max_value=max_edad,
    value=(min_edad, max_edad),
    step=1
)

# ---- Aplicación simultánea de ambos filtros ----
df_filtrado = df[
    (df["ANIO_EGRESO"] >= rango_anio[0]) &
    (df["ANIO_EGRESO"] <= rango_anio[1]) &
    (df["EDAD"] >= rango_edad[0]) &
    (df["EDAD"] <= rango_edad[1])
]

# ---- Resumen de filtros ----
st.info(
    f"**Filtros aplicados:** Años {rango_anio[0]}–{rango_anio[1]} | "
    f"Edades {rango_edad[0]}–{rango_edad[1]} | "
    f"Registros filtrados: **{df_filtrado.shape[0]}**"
)


# ================================================================
# FUNCIONES SIN SCIPY (SPEARMAN MANUAL)
# ================================================================
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


# ================================================================
# ESTADÍSTICAS DESCRIPTIVAS
# ================================================================
st.subheader("Estadísticas Descriptivas (Filtradas)")

edad_prom = df_filtrado["EDAD"].mean()
edad_std = df_filtrado["EDAD"].std()
sexo_dist = df_filtrado["SEXO"].value_counts(normalize=True) * 100

col1, col2 = st.columns(2)

with col1:
    st.metric("Edad promedio", f"{edad_prom:.1f} años")
    st.metric("Desviación estándar", f"{edad_std:.1f}")

with col2:
    st.write("### Distribución por sexo (%)")
    st.write(
        pd.DataFrame({
            "Sexo": sexo_dist.index,
            "Porcentaje": sexo_dist.values.round(1)
        })
    )


# ================================================================
# CORRELACIÓN SPEARMAN
# ================================================================
st.subheader("Correlación de Spearman (Filtro aplicado)")

rho = spearman_manual(df_filtrado["EDAD"], df_filtrado["NUMERO"])

if rho is None:
    st.warning("No es posible calcular Spearman con el rango seleccionado.")
else:
    st.info(f"**Coeficiente de Spearman:** `{rho:.3f}`")

# ===========================
# GRÁFICOS DEMOGRÁFICOS (2 COLUMNAS)
# ===========================
st.subheader("Gráficos Demográficos")

# Para acelerar render si hay muchos datos
df_plot = df_filtrado.sample(5000) if len(df_filtrado) > 5000 else df_filtrado

col_g1, col_g2 = st.columns(2)

# ---- COLUMNA 1 ----
with col_g1:
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.hist(df_plot["EDAD"], bins=20)
    ax1.set_title("Distribución de edades")
    ax1.set_xlabel("Edad")
    ax1.set_ylabel("Frecuencia")
    st.pyplot(fig1)

# ---- COLUMNA 2 ----
with col_g2:
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    df_plot["SEXO"].value_counts().plot(kind="bar", ax=ax2)
    ax2.set_title("Distribución por sexo")
    ax2.set_xlabel("Sexo")
    ax2.set_ylabel("Frecuencia")
    st.pyplot(fig2)

# ================================================================
# INTERPRETACIÓN AUTOMÁTICA
# ================================================================
#st.subheader("Interpretación Automática")

#interpretacion = f"""
#**Hallazgos Cuantitativos (filtros aplicados):**

#- Edad promedio: **{edad_prom:.1f} años**  
#- Desviación estándar: **{edad_std:.1f} años**  
#- Distribución por sexo:  
#  - Mujeres: **{sexo_dist.get('F', 0):.1f}%**  
#  - Hombres: **{sexo_dist.get('M', 0):.1f}%**  
#- Correlación de Spearman (Edad vs Número): **{rho if rho is not None else 'No calculable'}**

#**Interpretación:**  
#El análisis filtrado permite evaluar tendencias demográficas entre periodos y rangos de edad,
#aportando información útil para la gestión hospitalaria y validación de hipótesis de tu tesis.
#"""

#st.write(interpretacion)