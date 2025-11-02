#!/bin/bash
# Production Deployment Script for MTG Madness Carlo Simulator
# Run this script on your Ubuntu 22.04 server after initial setup

set -e  # Exit on any error

echo "🚀 MTG Madness Carlo - Production Deployment"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please create .env file with your configuration."
    echo "See PRODUCTION_DEPLOYMENT_GUIDE.md for details."
    exit 1
fi

echo -e "${GREEN}✓${NC} Found .env file"

# Check if AtomicCards.json exists
if [ ! -f backend/AtomicCards.json ]; then
    echo -e "${YELLOW}⚠${NC}  AtomicCards.json not found. Downloading..."
    cd backend
    wget -q --show-progress https://mtgjson.com/api/v5/AtomicCards.json
    cd ..
    echo -e "${GREEN}✓${NC} Downloaded AtomicCards.json"
else
    echo -e "${GREEN}✓${NC} Found AtomicCards.json"
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}⚠${NC}  Warning: Running as root. Consider using a non-root user with docker group access."
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo "Install it with: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is installed"

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available!${NC}"
    echo "Install it with: sudo apt install docker-compose-plugin"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker Compose is available"

# Source .env to check critical variables
source .env

# Check critical environment variables
MISSING_VARS=0

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ DOMAIN is not set in .env${NC}"
    MISSING_VARS=1
fi

if [ -z "$GOOGLE_CLIENT_ID" ]; then
    echo -e "${RED}❌ GOOGLE_CLIENT_ID is not set in .env${NC}"
    MISSING_VARS=1
fi

if [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo -e "${RED}❌ GOOGLE_CLIENT_SECRET is not set in .env${NC}"
    MISSING_VARS=1
fi

if [ -z "$CERTBOT_EMAIL" ]; then
    echo -e "${YELLOW}⚠${NC}  Warning: CERTBOT_EMAIL is not set. SSL setup may fail."
fi

if [ $MISSING_VARS -eq 1 ]; then
    echo ""
    echo -e "${RED}Please set missing variables in .env and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} All critical environment variables set"
echo ""

# Ask for confirmation
echo -e "${YELLOW}Domain: ${NC}$DOMAIN"
echo -e "${YELLOW}Email:  ${NC}${CERTBOT_EMAIL:-not set}"
echo ""
read -p "Deploy to production? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo "Starting deployment..."
echo ""

# Step 1: Initialize SSL certificates
echo "📜 Step 1: Setting up SSL certificates with Let's Encrypt..."
if [ -f ./init-letsencrypt.sh ]; then
    chmod +x ./init-letsencrypt.sh
    # Export environment variables for the SSL script
    export DOMAIN="${DOMAIN}"
    export SSL_EMAIL="${CERTBOT_EMAIL}"
    export SSL_STAGING="${SSL_STAGING:-1}"
    ./init-letsencrypt.sh
    echo -e "${GREEN}✓${NC} SSL certificates configured"
else
    echo -e "${YELLOW}⚠${NC}  init-letsencrypt.sh not found, skipping SSL setup"
    echo "   You'll need to configure SSL manually"
fi
echo ""

# Step 2: Build images
echo "🏗️  Step 2: Building Docker images..."
docker compose build --no-cache
echo -e "${GREEN}✓${NC} Docker images built"
echo ""

# Step 3: Start services
echo "🚀 Step 3: Starting services..."
docker compose up -d
echo -e "${GREEN}✓${NC} Services started"
echo ""

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Step 4: Check if services are running
echo "🔍 Step 4: Checking service health..."
SERVICES_OK=1

if ! docker compose ps | grep -q "backend.*Up"; then
    echo -e "${RED}❌ Backend is not running${NC}"
    SERVICES_OK=0
fi

if ! docker compose ps | grep -q "db.*Up"; then
    echo -e "${RED}❌ Database is not running${NC}"
    SERVICES_OK=0
fi

if ! docker compose ps | grep -q "frontend.*Up"; then
    echo -e "${RED}❌ Frontend is not running${NC}"
    SERVICES_OK=0
fi

if [ $SERVICES_OK -eq 0 ]; then
    echo ""
    echo -e "${RED}Some services failed to start. Check logs with:${NC}"
    echo "  docker compose logs"
    exit 1
fi

echo -e "${GREEN}✓${NC} All services are running"
echo ""

# Step 5: Run database migrations
echo "🗄️  Step 5: Running database migrations..."
docker compose exec -T backend alembic upgrade head
echo -e "${GREEN}✓${NC} Database migrations complete"
echo ""

# Step 6: Load default configuration
echo "⚙️  Step 6: Loading default configuration..."
docker compose exec -T backend python load_default_config.py --force
echo -e "${GREEN}✓${NC} Default configuration loaded"
echo ""

# Step 7: Verify deployment
echo "🔍 Step 7: Verifying deployment..."

# Check HTTP on port 81
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN:81 2>/dev/null || echo "000")
if [ "$HTTP_STATUS" -eq "301" ] || [ "$HTTP_STATUS" -eq "302" ] || [ "$HTTP_STATUS" -eq "200" ]; then
    echo -e "${GREEN}✓${NC} HTTP accessible on port 81 (status: $HTTP_STATUS)"
else
    echo -e "${YELLOW}⚠${NC}  HTTP status: $HTTP_STATUS (may be expected if SSL is not yet active)"
fi

# Check HTTPS on port 8443
HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN:8443 2>/dev/null || echo "000")
if [ "$HTTPS_STATUS" -eq "200" ]; then
    echo -e "${GREEN}✓${NC} HTTPS accessible on port 8443"
else
    echo -e "${YELLOW}⚠${NC}  HTTPS status: $HTTPS_STATUS (SSL may still be setting up)"
fi

# Check API health
API_HEALTH=$(curl -s https://$DOMAIN:8443/api/health 2>/dev/null || echo "")
if echo "$API_HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} API health check passed"
else
    echo -e "${YELLOW}⚠${NC}  API health check returned: $API_HEALTH"
fi

echo ""
echo "=============================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "=============================================="
echo ""
echo "🌐 Your application is available at:"
echo "   http://$DOMAIN:81  (HTTP)"
echo "   https://$DOMAIN:8443  (HTTPS)"
echo ""
echo "📊 Useful commands:"
echo "   docker compose ps              - Check service status"
echo "   docker compose logs -f         - View all logs"
echo "   docker compose logs -f backend - View backend logs"
echo "   docker compose restart         - Restart all services"
echo ""
echo "🔧 To update the application:"
echo "   git pull origin main"
echo "   docker compose build"
echo "   docker compose up -d"
echo ""
echo "📚 For more information, see:"
echo "   PRODUCTION_DEPLOYMENT_GUIDE.md"
echo ""

# Optional: Show service status
echo "Current service status:"
docker compose ps
echo ""

echo -e "${GREEN}Happy simulating! 🎲${NC}"

