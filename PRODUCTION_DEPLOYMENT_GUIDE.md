# Production Deployment Guide - Ubuntu 22.04

**Target**: Ubuntu 22.04 server with public IP  
**Goal**: Deploy MTG Madness Carlo Simulator with HTTPS and domain name  
**Date**: October 28, 2025

## Prerequisites

- ✅ Ubuntu 22.04 server with public IP address
- ✅ Domain name (e.g., `madnesscarlo.yourdomain.com`)
- ✅ SSH access to the server
- ✅ Google OAuth credentials (already have these)

## Overview

We'll deploy using Docker Compose, with:
- **Frontend**: React app served by Vite/Nginx
- **Backend**: FastAPI application
- **Database**: PostgreSQL
- **Cache/Queue**: Redis + Celery
- **Web Server**: Nginx as reverse proxy
- **SSL**: Let's Encrypt (automated)

## Part 1: Server Initial Setup

### 1.1 Connect to Your Server

```bash
# Replace with your server's IP
ssh your-username@YOUR_SERVER_IP

# Or if using a key:
ssh -i ~/.ssh/your-key.pem your-username@YOUR_SERVER_IP
```

### 1.2 Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.3 Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (to run docker without sudo)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version

# Log out and back in for group changes to take effect
exit
# Then SSH back in
```

### 1.4 Install Additional Dependencies

```bash
sudo apt install -y git curl wget ufw certbot python3-certbot-nginx
```

### 1.5 Configure Firewall

```bash
# Allow SSH (important! do this first)
sudo ufw allow ssh
sudo ufw allow 22/tcp

# Allow HTTP port 81 (for Madness app, not 80 due to Pi-hole)
sudo ufw allow 81/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

**Note**: This app uses **port 81** instead of the standard port 80 to avoid conflicts with other services like Pi-hole.

## Part 2: Domain Name Configuration

### 2.1 Configure DNS Records

**In your domain registrar's DNS settings** (GoDaddy, Namecheap, Cloudflare, etc.):

Add an **A record**:
- **Type**: A
- **Name**: `madnesscarlo` (or `@` for root domain, or `*` for wildcard)
- **Value**: `YOUR_SERVER_IP`
- **TTL**: 3600 (or automatic)

**Example configurations**:

| Record Type | Name | Value | Result |
|-------------|------|-------|--------|
| A | madnesscarlo | 123.45.67.89 | madnesscarlo.yourdomain.com |
| A | @ | 123.45.67.89 | yourdomain.com |
| CNAME | www | madnesscarlo.yourdomain.com | www.yourdomain.com |

**DNS Propagation**: Takes 5 minutes to 48 hours (usually < 1 hour)

**Check DNS propagation**:
```bash
# From your local machine:
nslookup madnesscarlo.yourdomain.com
dig madnesscarlo.yourdomain.com

# Should return your server's IP
```

### 2.2 Verify Domain Points to Server

```bash
# On the server:
curl ifconfig.me  # Get your server's public IP

# From your local machine:
ping madnesscarlo.yourdomain.com  # Should ping your server IP
```

## Part 3: Clone and Configure Application

### 3.1 Clone Repository

```bash
# Create app directory
cd ~
mkdir -p apps
cd apps

# Clone the repository
git clone https://github.com/bwhalley/madnesscarlo.git
cd madnesscarlo

# Checkout main branch (should be default)
git checkout main
```

### 3.2 Create Environment Variables

```bash
# Create .env file for production
cat > .env << 'EOF'
# Database
POSTGRES_USER=madness_user
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD_12345
POSTGRES_DB=madness_carlo
DATABASE_URL=postgresql://madness_user:CHANGE_THIS_PASSWORD_12345@db:5432/madness_carlo

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=CHANGE_THIS_TO_RANDOM_SECRET_KEY_67890
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here

# Domain (IMPORTANT!)
DOMAIN=madnesscarlo.yourdomain.com
FRONTEND_URL=https://madnesscarlo.yourdomain.com
BACKEND_URL=https://madnesscarlo.yourdomain.com

# Certbot Email
CERTBOT_EMAIL=your-email@example.com
EOF

# Generate a secure SECRET_KEY
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env

# Generate a secure POSTGRES_PASSWORD
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)" >> .env

# Edit the .env file with your actual values
nano .env
# OR
vim .env
```

**Important values to update**:
1. `GOOGLE_CLIENT_ID` - Your Google OAuth client ID
2. `GOOGLE_CLIENT_SECRET` - Your Google OAuth client secret
3. `DOMAIN` - Your actual domain name
4. `CERTBOT_EMAIL` - Your email for Let's Encrypt

### 3.3 Update OAuth Redirect URIs

**⚠️ CRITICAL STEP**: Update Google Cloud Console with production URL

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID
3. Add **Authorized JavaScript origins**:
   ```
   https://madnesscarlo.yourdomain.com
   ```
4. Add **Authorized redirect URIs**:
   ```
   https://madnesscarlo.yourdomain.com/auth/callback
   ```
5. Click **Save**

### 3.4 Download AtomicCards.json

```bash
# Create backend directory if needed
cd ~/apps/madnesscarlo/backend

# Download AtomicCards.json (large file, ~120MB)
wget https://mtgjson.com/api/v5/AtomicCards.json

# Verify it downloaded
ls -lh AtomicCards.json
# Should show ~120MB file
```

## Part 4: SSL Setup with Let's Encrypt

### 4.1 Ensure Domain is Resolving

```bash
# Verify domain points to this server
ping -c 3 madnesscarlo.yourdomain.com
# Should show your server's IP
```

### 4.2 Update SSL Initialization Script

```bash
cd ~/apps/madnesscarlo

# The init-letsencrypt.sh script should already exist
# Update domain in the script
sed -i 's/example.com/madnesscarlo.yourdomain.com/g' init-letsencrypt.sh

# Update email in the script
sed -i 's/your-email@example.com/your-actual-email@example.com/g' init-letsencrypt.sh

# Make it executable
chmod +x init-letsencrypt.sh
```

### 4.3 Update Nginx Configuration

```bash
cd ~/apps/madnesscarlo

# Update nginx configuration with your domain
# Edit nginx/default.conf or nginx/app.conf
nano nginx/default.conf
```

Update the `server_name` directives:
```nginx
server_name madnesscarlo.yourdomain.com;
```

## Part 5: Build and Deploy

### 5.1 Create Production Docker Compose Override

```bash
cd ~/apps/madnesscarlo

# Create docker-compose.prod.yml for production-specific settings
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  frontend:
    restart: always
    environment:
      - NODE_ENV=production
      - VITE_API_URL=https://madnesscarlo.yourdomain.com
      - VITE_WS_URL=wss://madnesscarlo.yourdomain.com

  backend:
    restart: always
    environment:
      - ENVIRONMENT=production

  db:
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    restart: always

  celery:
    restart: always

  nginx:
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
EOF

# Update with your actual domain
sed -i 's/madnesscarlo.yourdomain.com/YOUR_ACTUAL_DOMAIN/g' docker-compose.prod.yml
```

### 5.2 Initial SSL Certificate Setup

```bash
cd ~/apps/madnesscarlo

# Run the Let's Encrypt initialization script
./init-letsencrypt.sh

# This will:
# 1. Create dummy certificates
# 2. Start nginx
# 3. Request real certificates from Let's Encrypt
# 4. Reload nginx with real certificates
```

### 5.3 Build and Start Services

```bash
cd ~/apps/madnesscarlo

# Build the images
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start all services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check that all services are running
docker compose ps

# Check logs
docker compose logs -f backend
# Press Ctrl+C to exit logs
```

### 5.4 Initialize Database

```bash
# Run database migrations
docker compose exec backend alembic upgrade head

# Load default configuration
docker compose exec backend python load_default_config.py --force
```

## Part 6: Verify Deployment

### 6.1 Check Services

```bash
# Check all containers are running
docker compose ps

# Should show:
# - frontend (Up)
# - backend (Up)
# - db (Up)
# - redis (Up)
# - celery (Up)
# - nginx (Up)

# Check backend logs
docker compose logs backend --tail 50

# Check nginx logs
docker compose logs nginx --tail 50
```

### 6.2 Test Endpoints

```bash
# Test HTTPS redirect (should redirect to HTTPS)
curl -I http://madnesscarlo.yourdomain.com

# Test HTTPS (should return 200 OK)
curl -I https://madnesscarlo.yourdomain.com

# Test API health
curl https://madnesscarlo.yourdomain.com/api/health

# Test backend directly
curl https://madnesscarlo.yourdomain.com/api/docs
# Should return Swagger UI HTML
```

### 6.3 Access Application

Open in your browser:
```
https://madnesscarlo.yourdomain.com
```

**You should see**:
1. Green padlock (secure HTTPS)
2. Login screen
3. Google OAuth login button working
4. After login, all tabs functional

## Part 7: Maintenance and Monitoring

### 7.1 View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f celery
docker compose logs -f nginx

# Last N lines
docker compose logs backend --tail 100
```

### 7.2 Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
docker compose restart frontend
```

### 7.3 Update Application

```bash
cd ~/apps/madnesscarlo

# Pull latest code
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run any new migrations
docker compose exec backend alembic upgrade head
```

### 7.4 SSL Certificate Renewal

Certificates auto-renew via cron. To manually renew:

```bash
cd ~/apps/madnesscarlo

# Renew certificates
docker compose exec nginx certbot renew

# Reload nginx
docker compose exec nginx nginx -s reload
```

### 7.5 Database Backups

```bash
# Create backup
docker compose exec db pg_dump -U madness_user madness_carlo > backup_$(date +%Y%m%d).sql

# Restore backup
docker compose exec -T db psql -U madness_user madness_carlo < backup_20251028.sql
```

## Part 8: Troubleshooting

### Issue: Can't access site

**Check DNS**:
```bash
nslookup madnesscarlo.yourdomain.com
```

**Check firewall**:
```bash
sudo ufw status
# Ensure ports 80 and 443 are open
```

**Check nginx**:
```bash
docker compose logs nginx
```

### Issue: SSL certificate error

**Check Let's Encrypt logs**:
```bash
docker compose logs nginx | grep certbot
```

**Manually request certificate**:
```bash
./init-letsencrypt.sh
```

### Issue: OAuth not working

**Check redirect URIs** in Google Cloud Console match:
```
https://madnesscarlo.yourdomain.com/auth/callback
```

**Check environment variables**:
```bash
docker compose exec backend env | grep GOOGLE
docker compose exec backend env | grep FRONTEND_URL
```

### Issue: Backend not starting

**Check logs**:
```bash
docker compose logs backend
```

**Check database connection**:
```bash
docker compose exec backend python -c "from app.utils.database import engine; engine.connect()"
```

### Issue: Database connection failed

**Check database is running**:
```bash
docker compose ps db
```

**Check credentials in .env**:
```bash
cat .env | grep POSTGRES
```

## Part 9: Security Checklist

- ✅ Firewall configured (UFW)
- ✅ HTTPS enabled with Let's Encrypt
- ✅ Strong passwords for database
- ✅ Secret key is random and secure
- ✅ OAuth credentials are from environment variables
- ✅ Database not exposed to public internet
- ✅ Regular backups configured
- ✅ SSL certificates auto-renew

## Part 10: Performance Optimization

### Enable Gzip Compression

Already configured in nginx, but verify:
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

### Database Connection Pooling

Already configured in backend via SQLAlchemy.

### Redis Caching

Already in use for Celery and session management.

## Quick Reference Commands

```bash
# Navigate to app directory
cd ~/apps/madnesscarlo

# Check status
docker compose ps

# View logs
docker compose logs -f

# Restart services
docker compose restart

# Update application
git pull && docker compose build && docker compose up -d

# Backup database
docker compose exec db pg_dump -U madness_user madness_carlo > backup.sql

# Check disk space
df -h

# Check memory usage
free -h

# Monitor resources
docker stats
```

## Support

- **GitHub**: https://github.com/bwhalley/madnesscarlo
- **Logs**: `docker compose logs -f`
- **Health Check**: `curl https://yourdomain.com/api/health`

---

**🎉 Your MTG Madness Carlo Simulator is now live!**

Access it at: `https://madnesscarlo.yourdomain.com`

