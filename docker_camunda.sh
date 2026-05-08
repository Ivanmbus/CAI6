#!/bin/bash

echo "========================================"
echo "🚀 INSEGUS - Levantando Camunda"
echo "========================================"

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

# Verificar que Docker esté corriendo
if ! docker info &> /dev/null; then
    echo "❌ Docker Desktop no está ejecutándose"
    exit 1
fi

# Crear directorios
mkdir -p bpmn camunda-data

echo ""
echo "📦 Descargando e iniciando Camunda..."
echo "   Esto puede tomar unos minutos la primera vez"
echo ""

# Levantar Camunda
docker-compose up -d

echo ""
echo "========================================"
echo "✅ Camunda iniciado correctamente"
echo "========================================"
echo ""
echo "📌 Accesos:"
echo "   Cockpit: http://localhost:8080/camunda"
echo "   Tasklist: http://localhost:8080/camunda/tasklist"
echo "   REST API: http://localhost:8080/engine-rest"
echo ""
echo "   Usuario: demo"
echo "   Contraseña: demo"
echo ""
echo "💡 Ver logs: docker-compose logs -f"
echo "🛑 Detener: docker-compose down"
echo ""
echo "========================================"