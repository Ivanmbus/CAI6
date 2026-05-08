import csv
import requests
import json
from datetime import datetime

# ========== CONFIGURACIÓN ==========
CAMUNDA_URL = "http://localhost:8080/engine-rest"
PROCESS_DEFINITION_KEY = "proceso_compras_sanitarias"  # Cambiar por el ID real en Camunda
CSV_FILE = "asignaciones_balanceadas_final.csv"

# ========== FUNCIONES ==========
def iniciar_proceso_camunda(instancia_id, asignacion):
    """
    Inicia una instancia del proceso en Camunda con las variables de asignación
    """
    url = f"{CAMUNDA_URL}/process-definition/key/{PROCESS_DEFINITION_KEY}/start"
    
    # Construir el payload con las variables
    variables = {
        "instancia_id": {"value": instancia_id, "type": "Integer"},
        "empleado_t1": {"value": asignacion["T1"], "type": "String"},
        "empleado_t21": {"value": asignacion["T2.1"], "type": "String"},
        "empleado_t22": {"value": asignacion["T2.2"], "type": "String"},
        "empleado_t3": {"value": asignacion["T3"], "type": "String"},
        "empleado_t4": {"value": asignacion["T4"], "type": "String"},
        "fecha_inicio": {"value": datetime.now().isoformat(), "type": "String"}
    }
    
    payload = {
        "businessKey": f"compra_{instancia_id}",
        "variables": variables
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            print(f"✅ Instancia {instancia_id} creada correctamente")
            return True
        else:
            print(f"❌ Error en instancia {instancia_id}: HTTP {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def cargar_todas_instancias():
    """
    Lee el CSV y carga todas las instancias en Camunda
    """
    print("=" * 60)
    print("🚀 CARGANDO INSTANCIAS A CAMUNDA")
    print("=" * 60)
    
    # Verificar conexión con Camunda
    try:
        response = requests.get(f"{CAMUNDA_URL}/process-definition")
        if response.status_code != 200:
            print(f"❌ No se puede conectar a Camunda en {CAMUNDA_URL}")
            print("   Asegúrate de que Camunda esté ejecutándose")
            return False
        print(f"✅ Conexión con Camunda establecida")
    except:
        print(f"❌ No se puede conectar a Camunda en {CAMUNDA_URL}")
        print("   Ejecuta Camunda primero: docker run -d -p 8080:8080 camunda/camunda-bpm-platform:latest")
        return False
    
    # Leer CSV y cargar instancias
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        exito = 0
        error = 0
        
        for row in reader:
            instancia_id = int(row['Instancia'])
            asignacion = {
                "T1": row['T1'].split(' (')[0] if '(' in row['T1'] else row['T1'],
                "T2.1": row['T2.1'].split(' (')[0] if '(' in row['T2.1'] else row['T2.1'],
                "T2.2": row['T2.2'].split(' (')[0] if '(' in row['T2.2'] else row['T2.2'],
                "T3": row['T3'].split(' (')[0] if '(' in row['T3'] else row['T3'],
                "T4": row['T4'].split(' (')[0] if '(' in row['T4'] else row['T4']
            }
            
            if iniciar_proceso_camunda(instancia_id, asignacion):
                exito += 1
            else:
                error += 1
    
    print("=" * 60)
    print(f"📊 RESUMEN:")
    print(f"   ✅ Exitosas: {exito}")
    print(f"   ❌ Errores: {error}")
    print("=" * 60)

if __name__ == "__main__":
    cargar_todas_instancias()