import pandas as pd

# Nota: No ejecutar, solo pasar el script de limpia y muestra versión 2.
# -----------------------------
# RUTAS A LOS ARCHIVOS
# -----------------------------
input_path = r"D:\PROGRAMA DE TESIS 2025 - PREGRADO\DATASET EGRESOS HOSPITALARIOS INEN\Proyecto Tesis V1.0\data\Listado_egresos_hospitalarios_ene2022_jul2025.csv"
output_clean = r"D:\PROGRAMA DE TESIS 2025 - PREGRADO\DATASET EGRESOS HOSPITALARIOS INEN\Proyecto Tesis V1.0\data\listado_limpio.csv"
output_sample = r"D:\PROGRAMA DE TESIS 2025 - PREGRADO\DATASET EGRESOS HOSPITALARIOS INEN\Proyecto Tesis V1.0\data\muestra_egresos_10k.csv"

# -----------------------------
# CARGA DE DATOS
# -----------------------------
df = pd.read_csv(input_path, low_memory=False, encoding='latin1')
print("Datos cargados:", df.shape)
reporte = {}
reporte["Registros iniciales"] = len(df)

# -----------------------------
# LIMPIEZA DE DUPLICADOS
# -----------------------------
dup = df.duplicated().sum()
df = df.drop_duplicates()
reporte["Duplicados eliminados"] = dup

# -----------------------------
# NORMALIZAR NOMBRES DE COLUMNAS
# -----------------------------
df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")

print("\nColumnas detectadas después de limpieza:")
for col in df.columns:
    print(f" - {col}")

# -----------------------------
# LIMPIEZA DE FECHA DE EGRESO
# -----------------------------
fecha_cols = [c for c in df.columns if "FECHA" in c and "EGRESO" in c]

if fecha_cols:
    fecha_col = fecha_cols[0]
    print(f"\nColumna de fecha detectada: {fecha_col}")

    df[fecha_col] = pd.to_datetime(df[fecha_col], errors='coerce')
    n_invalid = df[fecha_col].isna().sum()

    df = df.dropna(subset=[fecha_col])
    reporte["Fechas de egreso inválidas eliminadas"] = n_invalid
else:
    print("\nNo se encontró columna de fecha de egreso.")
    fecha_col = None

# -----------------------------
# LIMPIEZA DE EDAD
# -----------------------------
edad_cols = [c for c in df.columns if "EDAD" in c]
if edad_cols:
    edad_col = edad_cols[0]
    print(f"Columna de edad detectada: {edad_col}")

    df[edad_col] = pd.to_numeric(df[edad_col], errors='coerce')

    antes = len(df)
    df = df[(df[edad_col].isna()) | ((df[edad_col] >= 0) & (df[edad_col] <= 120))]
    reporte["Edades fuera de rango eliminadas"] = antes - len(df)

# -----------------------------
# LIMPIEZA DE SEXO
# -----------------------------
sexo_cols = [c for c in df.columns if "SEXO" in c]
if sexo_cols:
    sexo_col = sexo_cols[0]
    print(f"Columna de sexo detectada: {sexo_col}")

    df[sexo_col] = df[sexo_col].astype(str).str.strip().str.upper()
    df[sexo_col] = df[sexo_col].replace({"MASCULINO": "M", "FEMENINO": "F"})

    antes = len(df)
    df = df[df[sexo_col].isin(["M", "F"])]
    reporte["Registros con sexo inválido eliminados"] = antes - len(df)
else:
    print("No se encontró ninguna columna de sexo.")

# -----------------------------
# ELIMINAR REGISTROS TOTALMENTE NULOS O VACÍOS
# -----------------------------
antes = len(df)
df = df.dropna(how="all")
reporte["Registros totalmente vacíos eliminados"] = antes - len(df)

# -----------------------------
# ELIMINAR FILAS CON NULOS EN CAMPOS IMPORTANTES
# -----------------------------
campos_clave = ["DEPARTAMENTO", "PROVINCIA", "DISTRITO"] if set(["DEPARTAMENTO", "PROVINCIA", "DISTRITO"]).issubset(df.columns) else []

for campo in campos_clave:
    antes = len(df)
    df = df[df[campo].notna()]
    reporte[f"Nulos eliminados en {campo}"] = antes - len(df)

# -----------------------------
# AGREGAR FILA FINAL CON TOTAL
# -----------------------------
total_registros = len(df)
print(f"\nTotal de registros después de limpieza: {total_registros}")

fila_total = {col: "" for col in df.columns}
fila_total[list(df.columns)[0]] = "TOTAL_REGISTROS"
fila_total[list(df.columns)[1]] = total_registros

df = pd.concat([df, pd.DataFrame([fila_total])], ignore_index=True)

# -----------------------------
# GUARDAR ARCHIVOS
# -----------------------------
df.to_csv(output_clean, index=False, encoding='utf-8-sig')
print("\n Archivo limpio guardado en:", output_clean)

sample = df.sample(n=10000, random_state=42) if len(df) > 10000 else df
sample.to_csv(output_sample, index=False, encoding='utf-8-sig')
print("Muestra guardada en:", output_sample)

# -----------------------------
# REPORTE FINAL
# -----------------------------
print("\n===== REPORTE DE LIMPIEZA =====")
for k, v in reporte.items():
    print(f"• {k}: {v}")

print("\nProceso completado correctamente.")