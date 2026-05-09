import pandas as pd
import numpy as np

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
ARCHIVO_CSV = 'resultados_escenario_1.csv'
UMBRAL_SLA_MS = 500.0  # El límite de latencia aceptable (ajústalo según tu línea base)

# ==========================================
# 2. CARGA Y PREPROCESAMIENTO DE DATOS
# ==========================================
print("Cargando datos de k6...")
# K6 exporta muchas métricas, solo nos interesa la duración de las peticiones HTTP
df = pd.read_csv(ARCHIVO_CSV)
df_req = df[df['metric_name'] == 'http_req_duration'].copy()

# Convertir el timestamp (que viene en epoch Unix) a un formato de fecha y hora real
df_req['timestamp'] = pd.to_datetime(df_req['timestamp'], unit='s')

# ==========================================
# 3. CÁLCULO DE LA MÉTRICA p95 POR SEGUNDO
# ==========================================
print("Calculando latencia p95 por segundo...")
# Agrupamos los datos cada 1 segundo ('1S') y calculamos el percentil 95
# Esto nos da una serie de tiempo suavizada y representativa
latencia_p95 = df_req.set_index('timestamp')['metric_value'].resample('1s').quantile(0.95)

# Llenamos posibles huecos donde no hubo peticiones (forward fill)
latencia_p95 = latencia_p95.ffill()

# ==========================================
# 4. DETERMINACIÓN DEL MTTR
# ==========================================
print("Analizando violaciones de SLA y calculando MTTR...")

# Encontrar los momentos donde el SLA fue violado
violaciones = latencia_p95[latencia_p95 > UMBRAL_SLA_MS]

if violaciones.empty:
    print("¡Genial! No hubo violaciones del SLA. El sistema soportó la carga.")
else:
    # T_falla: El primer instante donde la latencia superó el umbral
    t_falla = violaciones.index[0]
    
    # Para T_recuperacion: Buscamos cuándo la latencia vuelve a estar por debajo del umbral 
    # DESPUÉS del momento de la falla
    datos_post_falla = latencia_p95[latencia_p95.index > t_falla]
    recuperaciones = datos_post_falla[datos_post_falla <= UMBRAL_SLA_MS]
    
    if recuperaciones.empty:
        print("CRÍTICO: El sistema nunca se recuperó durante la prueba.")
    else:
        # T_recuperacion: El primer instante donde se estabiliza post-falla
        t_recuperacion = recuperaciones.index[0]
        
        # Calcular el MTTR en segundos
        mttr = (t_recuperacion - t_falla).total_seconds()
        
        print("-" * 40)
        print("RESULTADOS DEL EXPERIMENTO:")
        print(f"Inicio de la degradación (T_falla): {t_falla}")
        print(f"Recuperación del sistema (T_recup): {t_recuperacion}")
        print(f"MTTR (Tiempo Medio de Recuperación): {mttr} segundos")
        print("-" * 40)