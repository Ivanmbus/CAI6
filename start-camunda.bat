@echo off
setlocal enabledelayedexpansion

echo ========================================
echo 🚀 INSEGUS - Despliegue Automático de Camunda
echo ========================================
echo.


:deploy_bpmn

REM  Desplegar el archivo BPMN
echo.
echo [5/5] Desplegando proceso BPMN...



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