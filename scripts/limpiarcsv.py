import pandas as pd
import re
from pathlib import Path

# Correección del CSV base

ruta_entrada = Path(r"D:\PROGRAMA DE TESIS 2025 - PREGRADO\DATASET EGRESOS HOSPITALARIOS INEN\Proyecto Tesis V1.0\data\Listado_egresos_hospitalarios_ene2022_jul2025.csv")
ruta_salida = ruta_entrada.with_name(ruta_entrada.stem + "_corregido.csv")

print("\n=== INICIANDO CORRECCIÓN DE CSV ORIGINAL ===")

# Leer como texto crudo
with open(ruta_entrada, 'r', encoding='latin-1') as f:
    contenido = f.read()

# Quitar comillas dobles repetidas
contenido = re.sub(r'""', '"', contenido)

# Quitar comillas al inicio y fin de cada línea
contenido = re.sub(r'^\s*"', '', contenido, flags=re.MULTILINE)
contenido = re.sub(r'"\s*$', '', contenido, flags=re.MULTILINE)

# Guardar versión corregida
with open(ruta_salida, 'w', encoding='utf-8', newline='\n') as f:
    f.write(contenido)

print(f"✔ CSV corregido guardado en: {ruta_salida}")

# carga del csv corregido

df = pd.read_csv(ruta_salida, encoding="utf-8")
registros_iniciales = len(df)

print(f"\n📥 Datos cargados: {df.shape}")
print(f"Columnas detectadas: {list(df.columns)}")

# Normalización de las columnas

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.upper()
    .str.replace(" ", "_")
    .str.replace(r"[^A-Z0-9_]", "", regex=True)
)

print("\n🔧 Columnas normalizadas:")
print(df.columns.tolist())

# Limpieza de datos nulos, vacios y duplicados

reporte_invalidos = {}

for col in df.columns:
    serie = df[col].astype(str).str.strip().str.upper()
    reporte_invalidos[col] = serie.isin(["", "NONE", "NULL", "NAN"]).sum()

# Reemplazar valores vacíos/nulos explícitos
df = df.replace({
    "": None,
    " ": None,
    "NONE": None,
    "NULL": None,
    "nan": None,
    "NaN": None
})

# Eliminar duplicados
df = df.drop_duplicates()

# Eliminar filas con valores faltantes
df = df.dropna(how="any")

print("\n✔ Limpieza de nulos y duplicados completada")

# Corrección del formato de fechas

def limpiar_fecha(col):
    if col not in df.columns:
        return

    print(f"📅 Corrigiendo fecha: {col}")

    s = df[col].astype(str).str.replace(r'\D', '', regex=True)

    df[col] = pd.to_datetime(s, format='%Y%m%d', errors='coerce')
    df.dropna(subset=[col], inplace=True)

for col in ["FECHA_INGRESO", "FECHA_EGRESO", "FECHA_CORTE"]:
    limpiar_fecha(col)

# Correcció formato de edad

if "EDAD" in df.columns:
    print("👶 Corrigiendo EDAD...")
    df["EDAD"] = pd.to_numeric(df["EDAD"], errors="coerce")
    df = df[(df["EDAD"] >= 0) & (df["EDAD"] <= 120)]

# Corrección del formato de sexo

if "SEXO" in df.columns:
    print("🧍 Corrigiendo SEXO...")
    df["SEXO"] = df["SEXO"].astype(str).str.upper().str.strip()
    df["SEXO"] = df["SEXO"].replace({
        "FEMENINO": "F",
        "MASCULINO": "M",
        "F": "F",
        "M": "M"
    })
    df = df[df["SEXO"].isin(["M", "F"])]

# Reporte final

registros_finales = len(df)
eliminados = registros_iniciales - registros_finales

print("\n========================")
print("📊 REPORTE DE LIMPIEZA")
print("========================")
print(f"Registros iniciales:  {registros_iniciales}")
print(f"Registros finales:    {registros_finales}")
print(f"Eliminados:           {eliminados}")
print(f"Porcentaje eliminado: {100 * eliminados / registros_iniciales:.2f}%")

print("\n📌 Valores inválidos detectados (antes de limpiar):")
for col, cant in reporte_invalidos.items():
    print(f" - {col}: {cant}")

# Ruta de guaradado del archivo posterior al filtro de validacion de datos

ruta_final = ruta_entrada.with_name("dataset_limpio.csv")
df.to_csv(ruta_final, index=False, encoding="utf-8-sig")

print(f"\n💾 Archivo limpio guardado en: {ruta_final}")
print("✅ Proceso finalizado sin errores.\n")