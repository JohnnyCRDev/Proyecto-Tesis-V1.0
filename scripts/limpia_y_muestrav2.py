import os
import pandas as pd

# Ruta del archivo a procesar
BASE = r"D:\PROGRAMA DE TESIS 2025 - PREGRADO\DATASET EGRESOS HOSPITALARIOS INEN\Proyecto Tesis V1.0"
input_path = os.path.join(BASE, "data", "Listado_egresos_hospitalarios_ene2022_jul2025_corregido.csv")
output_clean = os.path.join(BASE, "data", "listado_limpio.csv")
output_sample = os.path.join(BASE, "data", "muestra_egresos_10k.csv")

# Carga segura del archivo
try:
    df = pd.read_csv(input_path, low_memory=False, encoding='utf-8-sig')
except UnicodeDecodeError:
    print("⚠️ Error con UTF-8, intentando con Latin-1...")
    df = pd.read_csv(input_path, low_memory=False, encoding='latin1')

registros_iniciales = len(df)
print("✅ Datos cargados:", df.shape)

# Normalización de Encabezados
df = df.drop_duplicates()

df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.upper()
    .str.replace(" ", "_")
    .str.replace(r"[^A-Z0-9_]", "", regex=True)
)

print("\n📋 Columnas tras normalizar:")
for c in df.columns:
    print(" -", c)

# Reporte de valores invalidos por cada columna
reporte_columnas = {}

def contar_invalidos(col):
    serie_raw = df[col]

    # NaN reales
    n_nan_real = serie_raw.isna().sum()

    # strings vacíos o nulos
    mask_notna = ~serie_raw.isna()
    s = serie_raw[mask_notna].astype(str).str.strip().str.upper()
    n_bad_strings = s.isin(["", "NAN", "NONE", "NULL"]).sum()

    return int(n_nan_real + n_bad_strings)

for col in df.columns:
    reporte_columnas[col] = contar_invalidos(col)

# Limpieza de datos general para registros con archivos nulos
df = df.replace({"": None, " ": None, "nan": None, "None": None, "NULL": None})
df = df.dropna(how="any")

# Parseo de la fecha de ingreso
fecha_cols1 = [c for c in df.columns if "FECHA" in c and "INGRESO" in c]
if fecha_cols1:
    fecha_col1 = fecha_cols1[0]
    print(f"\n📅 Columna de fecha detectada: {fecha_col1}")

    s = df[fecha_col1].astype(str).str.strip().str.replace(r'\D', '', regex=True)
    s = s.str.replace(r'\.0+$', '', regex=True)

    parsed = pd.to_datetime(s, format='%Y%m%d', errors='coerce')

    mask_nat = parsed.isna()
    parsed.loc[mask_nat] = pd.to_datetime(df.loc[mask_nat, fecha_col1], errors='coerce', dayfirst=True)

    df[fecha_col1] = parsed
    df = df.dropna(subset=[fecha_col1])

else:
    print("⚠️ No se encontró columna de fecha de ingreso.")

# Parseo de fecha de egreso
fecha_cols2 = [c for c in df.columns if "FECHA" in c and "EGRESO" in c]
if fecha_cols2:
    fecha_col2 = fecha_cols2[0]
    print(f"\n📅 Columna de fecha detectada: {fecha_col2}")

    s = df[fecha_col2].astype(str).str.strip().str.replace(r'\D', '', regex=True)
    s = s.str.replace(r'\.0+$', '', regex=True)

    parsed = pd.to_datetime(s, format='%Y%m%d', errors='coerce')

    mask_nat = parsed.isna()
    parsed.loc[mask_nat] = pd.to_datetime(df.loc[mask_nat, fecha_col2], errors='coerce', dayfirst=True)

    df[fecha_col2] = parsed
    df = df.dropna(subset=[fecha_col2])
else:
    print("⚠️ No se encontró columna de fecha de egreso.")

# Extracción de año y mes para los filtros
if fecha_cols1:
    df["ANIO_INGRESO"] = df[fecha_col1].dt.year
    df["MES_INGRESO"] = df[fecha_col1].dt.month

if fecha_cols2:
    df["ANIO_EGRESO"] = df[fecha_col2].dt.year
    df["MES_EGRESO"] = df[fecha_col2].dt.month

# Extracción de edad
edad_cols = [c for c in df.columns if "EDAD" in c]
if edad_cols:
    col_edad = edad_cols[0]
    df[col_edad] = pd.to_numeric(df[col_edad], errors='coerce')
    df = df[(df[col_edad].isna()) | ((df[col_edad] >= 0) & (df[col_edad] <= 120))]
    print(f"\n👶 Columna de edad detectada: {col_edad}")

# Extracción de sexo
sexo_cols = [c for c in df.columns if "SEXO" in c]
if sexo_cols:
    col_sexo = sexo_cols[0]
    df[col_sexo] = df[col_sexo].astype(str).str.strip().str.upper()
    df[col_sexo] = df[col_sexo].replace({
        'MASCULINO': 'M', 'FEMENINO': 'F',
        'MAS': 'M', 'FEM': 'F'
    })
    print(f"🧍 Columna de sexo detectada: {col_sexo}")

# Extracción y división del lugar de residencia en Departamento, Provincia y Distrito 
col_lugar = None
for col in df.columns:
    c = col.strip().upper()
    if c == 'LUGAR_RESIDENCIA':
        col_lugar = col
        break
    elif 'UBIGEO' in c and col_lugar is None:
        col_lugar = col

if col_lugar:
    print(f"\n📍 Columna de lugar detectada: {col_lugar}")

    df[col_lugar] = df[col_lugar].astype(str).str.strip().str.upper()

    split_df = df[col_lugar].str.split(r'\s*-\s*|/|\|', n=2, expand=True)

    df['DEPARTAMENTO'] = split_df[0].str.strip().replace({'': None})
    df['PROVINCIA'] = split_df[1].str.strip().replace({'': None}) if split_df.shape[1] > 1 else None
    df['DISTRITO'] = split_df[2].str.strip().replace({'': None}) if split_df.shape[1] > 2 else None

    print("✅ División de lugar completada.")
else:
    print("\n⚠️ No se encontró columna de lugar ni UBIGEO.")

# Reporte final de lo realizado en el filtro de validacion de datos
registros_finales = len(df)
eliminados = registros_iniciales - registros_finales
porcentaje = (eliminados / registros_iniciales) * 100

print("\n📊 ===== REPORTE DE LIMPIEZA =====")
print(f"Registros iniciales: {registros_iniciales}")
print(f"Registros finales:   {registros_finales}")
print(f"Registros eliminados: {eliminados}")
print(f"Porcentaje eliminado: {porcentaje:.2f}%")

print("\n📌 Valores inválidos detectados por columna (antes de limpiar):")
for col, n in reporte_columnas.items():
    pct = (n / registros_iniciales * 100) if registros_iniciales else 0
    print(f" - {col}: {n} inválidos ({pct:.2f}%)")

# Conteo del total de resgistos despues de la limpieza
cols = list(df.columns)

if len(cols) < 2:
    if 'TOTAL_REGISTROS' not in df.columns:
        df['TOTAL_REGISTROS'] = pd.NA
    if 'COUNT' not in df.columns:
        df['COUNT'] = pd.NA
    cols = list(df.columns)

fila_total = {col: "" for col in cols}
fila_total[cols[0]] = "TOTAL_REGISTROS"
fila_total[cols[1]] = registros_finales

df = pd.concat([df, pd.DataFrame([fila_total])], ignore_index=True)

# Ubicación de donde se guarda el archivo posterior filtro de validacion de datos
df.to_csv(output_clean, index=False, encoding='utf-8-sig')
print(f"\n💾 Archivo limpio guardado en: {output_clean}")

sample = df.sample(n=10000, random_state=42) if registros_finales > 10000 else df
sample.to_csv(output_sample, index=False, encoding='utf-8-sig')
print(f"📄 Muestra guardada en: {output_sample}")

print("\n✅ Proceso completado con éxito.")