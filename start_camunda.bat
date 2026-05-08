@echo off
echo ========================================
echo 🚀 INSEGUS - Levantando Camunda
echo ========================================

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está instalado
    echo    Descargar desde: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

REM Verificar si Docker está corriendo
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Desktop no está ejecutándose
    echo    Por favor, inicia Docker Desktop primero
    pause
    exit /b 1
)

REM Crear directorios necesarios
if not exist "bpmn" mkdir bpmn
if not exist "camunda-data" mkdir camunda-data

echo.
echo 📦 Descargando e iniciando Camunda...
echo    Esto puede tomar unos minutos la primera vez
echo.

REM Levantar Camunda con docker-compose
docker-compose up -d

echo.
echo ========================================
echo ✅ Camunda iniciado correctamente
echo ========================================
echo.
echo 📌 Accesos:
echo    Cockpit: http://localhost:8080/camunda
echo    Tasklist: http://localhost:8080/camunda/tasklist
echo    REST API: http://localhost:8080/engine-rest
echo.
echo    Usuario: demo
echo    Contraseña: demo
echo.
echo 💡 Para ver los logs:
echo    docker-compose logs -f
echo.
echo 🛑 Para detener Camunda:
echo    docker-compose down
echo.
echo ========================================
pause