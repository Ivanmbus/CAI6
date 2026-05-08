@echo off
setlocal enabledelayedexpansion

echo ========================================
echo 🚀 INSEGUS - Despliegue Automático de Camunda
echo ========================================
echo.

REM 1. Verificar Docker
echo [1/5] Verificando Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo  Docker no esta instalado
    echo    Descargar desde: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)
echo ✅ Docker OK
echo.

REM 2. Crear directorio para BPMN si no existe
echo [2/5] Preparando directorios...
if not exist "bpmn" mkdir bpmn
echo  Directorio bpmn/ listo
echo.

REM 3. Levantar Camunda con docker-compose
echo [3/5] Iniciando Camunda...
docker-compose up -d
if errorlevel 1 (
    echo  Error al iniciar Camunda
    pause
    exit /b 1
)
echo  Contenedor iniciado
echo.

REM 4. Esperar a que Camunda esté completamente listo
echo [4/5] Esperando a que Camunda esté listo...
echo     (Esto puede tomar 30-60 segundos)

set MAX_ATTEMPTS=30
set ATTEMPT=0
set READY=0

:wait_loop
set /a ATTEMPT+=1
echo     Intento !ATTEMPT! de %MAX_ATTEMPTS%...

REM Verificar si el contenedor está corriendo
docker ps | findstr camunda-insegus >nul
if errorlevel 1 (
    echo     ⏳ Contenedor aún no está corriendo...
    timeout /t 3 /nobreak >nul
    goto check_continue
)

REM Verificar que la API REST responda
for /f %%i in ('curl -s -o nul -w "%%{http_code}" http://localhost:8080/engine-rest/version') do set STATUS=%%i

if "%STATUS%"=="200" (
    echo Camunda esta listo!
    set READY=1
    goto deploy_bpmn
) else (
    echo API aun no responde... [%STATUS%]
)

:check_continue
if !ATTEMPT! geq %MAX_ATTEMPTS% (
    echo ❌ Tiempo de espera agotado. Camunda no está listo.
    echo    Verifica con: docker-compose logs
    pause
    exit /b 1
)

timeout /t 3 /nobreak >nul
goto wait_loop

:deploy_bpmn

REM 5. Desplegar el archivo BPMN
echo.
echo [5/5] Desplegando proceso BPMN...

REM Verificar si existe el archivo BPMN
if not exist "bpmn\proceso_compras.bpmn" (
    echo ⚠️ No se encuentra bpmn/proceso_compras.bpmn
    echo    Creando archivo BPMN de ejemplo...
    call :crear_bpmn_ejemplo
)

REM Desplegar usando curl
curl -X POST http://localhost:8080/engine-rest/deployment/create ^
  -F "deployment-name=proceso_compras_sanitarias" ^
  -F "enable-duplicate-filtering=false" ^
  -F "deploy-changed-only=false" ^
  -F "data=@bpmn/proceso_compras.bpmn"

if errorlevel 1 (
    echo ❌ Error al desplegar BPMN
    pause
    exit /b 1
)

echo.
echo  BPMN desplegado correctamente
echo.

REM Mostrar resumen final
echo ========================================
echo  DESPLIEGUE COMPLETADO
echo ========================================
echo.
echo  ACCESOS:
echo    Cockpit: http://localhost:8080/camunda
echo    Tasklist: http://localhost:8080/camunda/tasklist
echo    REST API: http://localhost:8080/engine-rest
echo.
echo    Usuario: demo
echo    Contraseña: demo
echo.
echo  PROCESOS DISPONIBLES:
curl -s http://localhost:8080/engine-rest/process-definition | findstr "name"
echo.
echo ========================================
echo  Para cargar las 20 instancias:
echo    python cargar_a_camunda.py
echo.
echo  Para detener Camunda:
echo    docker-compose down
echo ========================================
pause
exit /b 0