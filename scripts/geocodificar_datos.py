import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

# Carga de datos
ruta_datos = r"D:\PROGRAMA DE TESIS 2025 - PREGRADO\DATASET EGRESOS HOSPITALARIOS INEN\Proyecto Tesis V1.0\data\listado_limpio.csv"
df = pd.read_csv(ruta_datos, encoding="latin1")
# Normalizar nombres
for col in ["DEPARTAMENTO", "PROVINCIA", "DISTRITO"]:
    df[col] = df[col].astype(str).str.upper().str.strip()
# Preparar geocodificador
geolocator = Nominatim(user_agent="geo_egresos", timeout=20)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3, error_wait_seconds=10)
# Crear dataframe de distritos únicos
df_distritos = df[["DEPARTAMENTO", "PROVINCIA", "DISTRITO"]].drop_duplicates().reset_index(drop=True)
df_distritos["LATITUD"] = None
df_distritos["LONGITUD"] = None
# Geocodificar distritos únicos
for idx, row in df_distritos.iterrows():
    location_str = f"{row['DISTRITO']}, {row['PROVINCIA']}, {row['DEPARTAMENTO']}, PERU"
    try:
        location = geocode(location_str)
        if location:
            df_distritos.at[idx, "LATITUD"] = location.latitude
            df_distritos.at[idx, "LONGITUD"] = location.longitude
            print(f"✅ Geocodificado: {location_str} -> ({location.latitude}, {location.longitude})")
        else:
            print(f"⚠ No encontrado: {location_str}")
    except Exception as e:
        print(f"❌ Error en {location_str}: {e}")
    time.sleep(1) 
# Guardar coordenadas
ruta_salida = r"D:\PROGRAMA DE TESIS 2025 - PREGRADO\DATASET EGRESOS HOSPITALARIOS INEN\Proyecto Tesis V1.0\data\coordenadas_distritos_peru.csv"
df_distritos.to_csv(ruta_salida, index=False, encoding="utf-8-sig")
print(f"📁 Coordenadas guardadas en: {ruta_salida}")