#!/bin/bash

# 🧬 Morphology Atlas - Script de Inicio Rápido
# Este script construye y arranca el contenedor Docker

set -e

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                    ║${NC}"
echo -e "${BLUE}║              🧬 DISMORPHOLOGY ATLAS - DOCKER SETUP                ║${NC}"
echo -e "${BLUE}║                                                                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker no está instalado. Por favor instala Docker primero.${NC}"
    exit 1
fi

# Verificar que docker compose está disponible
if ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}⚠️  docker compose no está disponible. Por favor instala Docker Compose primero.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker y Docker Compose detectados${NC}"
echo ""

# Construir la imagen
echo -e "${BLUE}📦 Construyendo imagen Docker...${NC}"
docker compose build

echo ""
echo -e "${GREEN}✅ Imagen construida exitosamente${NC}"
echo ""

# Arrancar el contenedor
echo -e "${BLUE}🚀 Arrancando contenedor...${NC}"
docker compose up -d

echo ""
echo -e "${GREEN}✅ Contenedor arrancado exitosamente${NC}"
echo ""

# Esperar a que el servicio esté listo
echo -e "${BLUE}⏳ Esperando a que el servicio esté listo...${NC}"
sleep 3

# Verificar el estado
if docker compose ps | grep -q "Up"; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                    ║${NC}"
    echo -e "${GREEN}║              ✅ DISMORPHOLOGY ATLAS ESTÁ CORRIENDO                 ║${NC}"
    echo -e "${GREEN}║                                                                    ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}🌐 Accede a la aplicación en:${NC}"
    echo -e "   ${GREEN}http://localhost:8888${NC}"
    echo ""
    echo -e "${BLUE}📊 Comandos útiles:${NC}"
    echo -e "   Ver logs:       ${YELLOW}docker compose logs -f${NC}"
    echo -e "   Detener:        ${YELLOW}docker compose stop${NC}"
    echo -e "   Reiniciar:      ${YELLOW}docker compose restart${NC}"
    echo -e "   Apagar y borrar: ${YELLOW}docker compose down${NC}"
    echo ""
else
    echo ""
    echo -e "${YELLOW}⚠️  Hubo un problema al arrancar el contenedor${NC}"
    echo -e "   Ejecuta: ${YELLOW}docker compose logs${NC} para ver los detalles"
    echo ""
    exit 1
fi
