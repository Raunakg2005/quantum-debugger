#!/bin/bash

# Quantum Circuit UI - Deployment Script for Ubuntu VPS
# Usage: ./deploy.sh [start|stop|restart|logs|rebuild]

set -e

COMPOSE_FILE="docker-compose.shared-mongo.yml"
SERVICE_NAME="quantum-ui"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Quantum Circuit UI - Deployment Manager${NC}\n"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Function definitions
start() {
    echo -e "${YELLOW}📦 Starting Quantum UI...${NC}"
    docker-compose -f $COMPOSE_FILE up -d --build
    echo -e "${GREEN}✅ Quantum UI started successfully!${NC}"
    echo -e "${GREEN}🌐 Access at: http://localhost:3000/quantum/${NC}"
}

stop() {
    echo -e "${YELLOW}🛑 Stopping Quantum UI...${NC}"
    docker-compose -f $COMPOSE_FILE down
    echo -e "${GREEN}✅ Quantum UI stopped${NC}"
}

restart() {
    echo -e "${YELLOW}🔄 Restarting Quantum UI...${NC}"
    stop
    start
}

logs() {
    echo -e "${YELLOW}📋 Showing logs (Ctrl+C to exit)...${NC}"
    docker logs -f $SERVICE_NAME
}

rebuild() {
    echo -e "${YELLOW}🔨 Rebuilding Quantum UI...${NC}"
    docker-compose -f $COMPOSE_FILE down
    docker-compose -f $COMPOSE_FILE build --no-cache
    docker-compose -f $COMPOSE_FILE up -d
    echo -e "${GREEN}✅ Rebuild complete!${NC}"
}

status() {
    echo -e "${YELLOW}📊 Service Status:${NC}"
    docker ps --filter "name=$SERVICE_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo -e "${YELLOW}💾 Resource Usage:${NC}"
    docker stats --no-stream $SERVICE_NAME
}

# Main script logic
case "${1:-start}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    rebuild)
        rebuild
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|rebuild|status}"
        exit 1
        ;;
esac
