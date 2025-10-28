#!/bin/bash
# Initial Server Setup Script for Ubuntu 22.04
# Run this script on a fresh Ubuntu 22.04 server

set -e  # Exit on any error

echo "🖥️  MTG Madness Carlo - Server Setup"
echo "====================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running on Ubuntu
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}❌ Cannot determine OS. This script is for Ubuntu 22.04.${NC}"
    exit 1
fi

source /etc/os-release
if [ "$ID" != "ubuntu" ]; then
    echo -e "${RED}❌ This script is designed for Ubuntu. Detected: $ID${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Running on Ubuntu $VERSION"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    echo "Usage: sudo bash server-setup.sh"
    exit 1
fi

echo "This script will:"
echo "  1. Update system packages"
echo "  2. Install Docker and Docker Compose"
echo "  3. Install Git and other tools"
echo "  4. Configure firewall (UFW)"
echo "  5. Create application directory"
echo ""

read -p "Continue? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi

# Step 1: Update system
echo "📦 Step 1: Updating system packages..."
apt update
apt upgrade -y
echo -e "${GREEN}✓${NC} System updated"
echo ""

# Step 2: Install Docker
echo "🐳 Step 2: Installing Docker..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker already installed"
else
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo -e "${GREEN}✓${NC} Docker installed"
fi

# Install Docker Compose plugin
if docker compose version &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose already installed"
else
    apt install -y docker-compose-plugin
    echo -e "${GREEN}✓${NC} Docker Compose installed"
fi
echo ""

# Step 3: Install additional tools
echo "🛠️  Step 3: Installing additional tools..."
apt install -y \
    git \
    curl \
    wget \
    ufw \
    certbot \
    python3-certbot-nginx \
    htop \
    vim \
    nano

echo -e "${GREEN}✓${NC} Tools installed"
echo ""

# Step 4: Configure firewall
echo "🔥 Step 4: Configuring firewall..."
# Reset UFW to start fresh
ufw --force reset

# Allow SSH (IMPORTANT!)
ufw allow 22/tcp
ufw allow ssh

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw --force enable

echo -e "${GREEN}✓${NC} Firewall configured"
ufw status
echo ""

# Step 5: Add current user to docker group (if not root)
if [ -n "$SUDO_USER" ]; then
    echo "👤 Step 5: Adding user $SUDO_USER to docker group..."
    usermod -aG docker $SUDO_USER
    echo -e "${GREEN}✓${NC} User added to docker group"
    echo -e "${YELLOW}⚠${NC}  Note: User must log out and back in for group changes to take effect"
else
    echo "👤 Step 5: Running as root, skipping user group setup"
fi
echo ""

# Step 6: Create application directory
echo "📁 Step 6: Creating application directory..."
if [ -n "$SUDO_USER" ]; then
    # Create in user's home directory
    USER_HOME=$(getent passwd $SUDO_USER | cut -d: -f6)
    APP_DIR="$USER_HOME/apps"
    mkdir -p $APP_DIR
    chown $SUDO_USER:$SUDO_USER $APP_DIR
    echo -e "${GREEN}✓${NC} Created $APP_DIR"
    echo ""
    echo "Next steps:"
    echo "  1. Log out and log back in (for docker group to take effect)"
    echo "  2. cd $APP_DIR"
    echo "  3. git clone https://github.com/bwhalley/madnesscarlo.git"
    echo "  4. cd madnesscarlo"
    echo "  5. Follow PRODUCTION_DEPLOYMENT_GUIDE.md"
else
    APP_DIR="/opt/madnesscarlo"
    mkdir -p $APP_DIR
    echo -e "${GREEN}✓${NC} Created $APP_DIR"
    echo ""
    echo "Next steps:"
    echo "  1. cd $APP_DIR"
    echo "  2. git clone https://github.com/bwhalley/madnesscarlo.git ."
    echo "  3. Follow PRODUCTION_DEPLOYMENT_GUIDE.md"
fi
echo ""

# Step 7: Display system info
echo "📊 System Information:"
echo "  OS: $PRETTY_NAME"
echo "  Docker: $(docker --version | cut -d' ' -f3)"
echo "  Docker Compose: $(docker compose version | cut -d' ' -f4)"
echo "  Git: $(git --version | cut -d' ' -f3)"
echo ""

# Step 8: Display firewall status
echo "🔥 Firewall Status:"
ufw status numbered
echo ""

echo "=============================================="
echo -e "${GREEN}✅ Server Setup Complete!${NC}"
echo "=============================================="
echo ""
echo "🎯 Quick Start Commands:"
echo ""
if [ -n "$SUDO_USER" ]; then
    echo "  # As user $SUDO_USER (after logging out and back in):"
    echo "  cd ~/apps"
else
    echo "  # As root or sudo user:"
    echo "  cd /opt/madnesscarlo"
fi
echo "  git clone https://github.com/bwhalley/madnesscarlo.git"
echo "  cd madnesscarlo"
echo "  cp env.production.template .env"
echo "  nano .env  # Edit with your values"
echo "  bash deploy-prod.sh"
echo ""
echo "📚 Documentation:"
echo "  PRODUCTION_DEPLOYMENT_GUIDE.md - Full deployment guide"
echo "  DEPLOYMENT_CHECKLIST.md - Quick checklist"
echo ""
echo -e "${GREEN}Ready to deploy! 🚀${NC}"

