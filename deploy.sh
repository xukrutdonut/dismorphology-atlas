#!/bin/bash

# Deploy script for Morphology Atlas
# Usage: ./deploy.sh [dev|prod]

set -e

ENVIRONMENT=${1:-dev}

echo "═══════════════════════════════════════════════════════════"
echo "  Deploying Morphology Atlas - Environment: $ENVIRONMENT"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    echo "❌ Error: Environment must be 'dev' or 'prod'"
    echo "   Usage: ./deploy.sh [dev|prod]"
    exit 1
fi

# Set variables based on environment
if [ "$ENVIRONMENT" = "dev" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
    DOMAIN="dev.neuropedialab.org"
    PORT="8888"
elif [ "$ENVIRONMENT" = "prod" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    DOMAIN="morpho.neuropedialab.org"
    PORT="80"
fi

echo "📋 Configuration:"
echo "   Environment: $ENVIRONMENT"
echo "   Domain: $DOMAIN"
echo "   Port: $PORT"
echo "   Compose file: $COMPOSE_FILE"
echo ""

# Stop existing container
echo "🛑 Stopping existing container..."
docker-compose -f $COMPOSE_FILE down 2>/dev/null || true
echo ""

# Build new image
echo "🔨 Building Docker image..."
docker-compose -f $COMPOSE_FILE build --no-cache
echo ""

# Start container
echo "🚀 Starting container..."
docker-compose -f $COMPOSE_FILE up -d
echo ""

# Wait for health check
echo "⏳ Waiting for container to be healthy..."
sleep 5

# Check status
if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  Morphology Atlas is running"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "🌐 Access URLs:"
    echo "   Local:  http://localhost:$PORT"
    echo "   Domain: http://$DOMAIN (configure DNS first)"
    echo ""
    echo "📊 Container status:"
    docker-compose -f $COMPOSE_FILE ps
    echo ""
    echo "📝 To view logs:"
    echo "   docker-compose -f $COMPOSE_FILE logs -f"
    echo ""
else
    echo ""
    echo "❌ Deployment failed!"
    echo "   Check logs with: docker-compose -f $COMPOSE_FILE logs"
    exit 1
fi
