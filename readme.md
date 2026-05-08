# 📚 README - INSEGUS: Control de Acceso Dinámico

## Requisitos previos

Se requiere sistema operativo Windows

| Componente | Versión |
|------------|---------|
| **Python** | 3.11 o 3.12 |
| **Docker Desktop** | Cualquier versión reciente |

---

## Instalación

### 1. Descomprimir el proyecto

### 2. Instalar dependencias:  Abrir terminal y ejecutar

**Bloque 1 (ZTNA):**
```bash
cd bloque1_ztna
pip install -r requirements.txt
```

**Script de carga a Camunda:** desde la raíz del proyecto ejecutar
```bash
pip install requests
```

---

## Bloque 1: ZTNA

### Generar certificados
```bash
cd bloque1_ztna
python generar_certificados_prueba.py
```

### Ejecutar (2 terminales)

**Terminal 1 - Broker:**
```bash
python broker_ztna.py
```

**Terminal 2 - Cliente:**
```bash
python cliente_ztna.py --rol medico
python cliente_ztna.py --rol enfermero
python cliente_ztna.py --rol admin
```

---

## Bloque 2: Generar CSV (20 instancias)

```bash
cd bloque2_camunda_offline
python generar_asignaciones.py
```

**Salida:** `asignaciones_compras.csv`

---

## Camunda: Despliegue y carga

### 1. Iniciar Camunda y cargar bpmn
Esperar a que el contenedor de camunda este levantado puede tardar unos 30 segundos
```bash
docker compose up -d
.\start_camunda.bat
```

### 2. Cargar las 20 instancias desde el CSV
```bash
python cargar_a_camunda.py
```

### 3. Detener Camunda cuando se quiera
```bash
docker-compose down
```

---

## Accesos Camunda

| URL | http://localhost:8080/camunda |
|-----|-------------------------------|
| **Usuario** | `demo` |
| **Contraseña** | `demo` |

---

## Comandos rápidos

| Tarea | Comando |
|-------|---------|
| Broker ZTNA | `cd bloque1_ztna && python broker_ztna.py` |
| Cliente ZTNA | `python cliente_ztna.py --rol medico` |
| Generar CSV | `cd bloque2_camunda_offline && python generar_asignaciones.py` |
| Iniciar Camunda | `start_camunda.bat` |
| Cargar instancias | `python cargar_a_camunda.py` |
| Detener Camunda | `docker-compose down` |

---

## Errores comunes

| Error | Solución |
|-------|----------|
| `No se encuentra certificado` | Ejecuta `python generar_certificados_correctos.py` |
| `Connection refused` | El broker no está corriendo |
| `Firma inválida` | Usa `broker_ztna_simplificado.py` |

---

**Proyecto INSEGUS - Mayo 2026**