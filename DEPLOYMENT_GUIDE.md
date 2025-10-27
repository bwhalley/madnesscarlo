# Production Deployment Guide

## Overview

This guide covers deploying the MTG Madness Carlo web application to a production server using Docker and Docker Compose.

## Prerequisites

- A Linux server (Ubuntu 22.04 LTS recommended)
- Docker and Docker Compose installed on the server
- A domain name (optional but recommended for SSL)
- Google OAuth credentials configured for your production domain

## 🚀 Quick Deployment Steps

### 1. Prepare Your Server

```bash
# SSH into your server
ssh user@your-server.com

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

# Log out and back in for group changes to take effect
exit
```

### 2. Clone Your Repository

```bash
# SSH back into your server
ssh user@your-server.com

# Clone the repository
git clone https://github.com/your-username/madnesscarlo.git
cd madnesscarlo

# Switch to your web-app branch
git checkout branch/web-app
```

### 3. Download AtomicCards.json

Since this file is not in the repository (it's too large), download it:

```bash
# In the project root
wget https://mtgjson.com/api/v5/AtomicCards.json

# Verify it downloaded
ls -lh AtomicCards.json
```

### 4. Configure Environment Variables

Create a production `.env` file:

```bash
cat > .env << 'EOF'
# Google OAuth Credentials (PRODUCTION URLs)
GOOGLE_CLIENT_ID=your-production-client-id
GOOGLE_CLIENT_SECRET=your-production-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/auth/google/callback

# Database (PostgreSQL)
POSTGRES_USER=madness_user
POSTGRES_PASSWORD=CHANGE_THIS_TO_STRONG_PASSWORD
POSTGRES_DB=madness_carlo
DATABASE_URL=postgresql://madness_user:CHANGE_THIS_TO_STRONG_PASSWORD@postgres:5432/madness_carlo

# Redis
REDIS_URL=redis://redis:6379/0

# JWT Secret (GENERATE A NEW STRONG SECRET)
SECRET_KEY=GENERATE_A_LONG_RANDOM_STRING_HERE
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Environment
ENVIRONMENT=production

# CORS (Update with your domain)
CORS_ORIGINS=["https://yourdomain.com"]
EOF

# Secure the .env file
chmod 600 .env
```

**Important:** Generate strong secrets!

```bash
# Generate a strong JWT secret
openssl rand -hex 32

# Generate a strong database password
openssl rand -base64 32
```

### 5. Update Google OAuth Redirect URIs

In your [Google Cloud Console](https://console.cloud.google.com/):

1. Navigate to **APIs & Services > Credentials**
2. Click on your OAuth 2.0 Client ID
3. Add to **Authorized redirect URIs**:
   - `https://yourdomain.com/api/auth/google/callback`
4. Add to **Authorized JavaScript origins**:
   - `https://yourdomain.com`
5. Click **Save**

### 6. Create Production Docker Compose Override (Optional)

For production-specific settings, create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    restart: always
    environment:
      - ENVIRONMENT=production
    
  frontend:
    restart: always
    
  postgres:
    restart: always
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
    
  redis:
    restart: always
    volumes:
      - redis_data_prod:/data
    
  celery-worker:
    restart: always

volumes:
  postgres_data_prod:
  redis_data_prod:
```

### 7. Build and Deploy

```bash
# Build images
docker-compose build

# Start services in detached mode
docker-compose up -d

# Or with production override:
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Check specific service
docker-compose logs backend --tail=50
```

### 8. Load Default Configuration

```bash
# Run the configuration loader
docker-compose exec backend python load_default_config.py --force

# Verify it loaded
docker-compose exec backend python -c "
from app.database import get_db
from app.models.simulation_config import SimulationConfig
db = next(get_db())
config = db.query(SimulationConfig).filter_by(is_default=True).first()
print(f'Default config: {config.name if config else \"Not found\"}')
"
```

### 9. Set Up Nginx Reverse Proxy (Recommended)

Install Nginx on your server:

```bash
sudo apt update
sudo apt install nginx

# Create site configuration
sudo nano /etc/nginx/sites-available/madnesscarlo
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket endpoint
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    client_max_body_size 10M;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/madnesscarlo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 10. Set Up SSL with Let's Encrypt

Install Certbot:

```bash
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

Certbot will automatically update your Nginx configuration for HTTPS.

## 🔒 Security Checklist

- [ ] Changed all default passwords
- [ ] Generated strong JWT secret (32+ characters)
- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Updated Google OAuth redirect URIs for production domain
- [ ] Secured `.env` file with `chmod 600`
- [ ] Enabled firewall (only allow 22, 80, 443)
- [ ] Set up SSL/HTTPS with Let's Encrypt
- [ ] Configured CORS_ORIGINS for your domain only
- [ ] Regular backups configured (see below)

### Configure Firewall

```bash
# Enable UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
sudo ufw status
```

## 📦 Database Backups

### Automated Daily Backups

Create a backup script:

```bash
sudo nano /usr/local/bin/backup-madness-db.sh
```

Add this content:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/madnesscarlo"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql.gz"

mkdir -p $BACKUP_DIR

# Backup database
docker-compose -f /home/user/madnesscarlo/docker-compose.yml exec -T postgres \
  pg_dump -U madness_user madness_carlo | gzip > $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

Make it executable:

```bash
sudo chmod +x /usr/local/bin/backup-madness-db.sh
```

Add to crontab:

```bash
sudo crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * /usr/local/bin/backup-madness-db.sh >> /var/log/madness-backup.log 2>&1
```

### Manual Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U madness_user madness_carlo > backup.sql

# Restore
docker-compose exec -T postgres psql -U madness_user madness_carlo < backup.sql
```

## 🔄 Updating the Application

### Pull and Deploy Updates

```bash
cd /home/user/madnesscarlo

# Pull latest changes
git pull origin branch/web-app

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Zero-Downtime Updates (Advanced)

For production, consider using Docker Swarm or Kubernetes for rolling updates.

## 📊 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Follow new logs only
docker-compose logs -f --tail=0
```

### Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up unused images/containers
docker system prune -a
```

### Health Checks

Create a monitoring script:

```bash
#!/bin/bash
# /usr/local/bin/check-madness-health.sh

# Check if services are running
services=("madness-backend" "madness-frontend" "madness-postgres" "madness-redis" "madness-celery-worker")

for service in "${services[@]}"; do
    if ! docker ps | grep -q $service; then
        echo "❌ $service is not running!"
        # Send alert (email, Slack, etc.)
    fi
done

# Check API health
if ! curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "❌ API health check failed!"
fi
```

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check specific service
docker-compose logs backend

# Restart services
docker-compose restart

# Full rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues

```bash
# Check database is running
docker-compose exec postgres psql -U madness_user -d madness_carlo -c "SELECT 1;"

# Check connection from backend
docker-compose exec backend python -c "
from app.database import engine
try:
    engine.connect()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

### Disk Space Issues

```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a --volumes

# Remove old logs
docker-compose logs --tail=0 > /dev/null
```

### Google OAuth Not Working

1. Verify redirect URI matches exactly in Google Cloud Console
2. Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
3. Ensure `GOOGLE_REDIRECT_URI` uses `https://` in production
4. Check browser console for CORS errors

### Check Container Health

```bash
# Inspect container
docker inspect madness-backend

# Enter container shell
docker-compose exec backend bash

# Check environment variables
docker-compose exec backend env | grep GOOGLE
```

## 🎯 Production Best Practices

1. **Use a Reverse Proxy**: Nginx or Caddy in front of your containers
2. **Enable SSL/HTTPS**: Let's Encrypt is free and automatic
3. **Monitor Logs**: Set up log aggregation (ELK stack, Grafana Loki)
4. **Set Resource Limits**: Add memory/CPU limits in docker-compose
5. **Health Checks**: Implement health check endpoints
6. **Backups**: Automate database backups
7. **Monitoring**: Use Prometheus + Grafana or similar
8. **Alerts**: Set up alerting for service failures
9. **Updates**: Regular security updates for base images
10. **Documentation**: Keep deployment docs updated

## 📝 Environment-Specific Configurations

### Development (Local)

- HTTP only (no SSL)
- Debug mode enabled
- Hot reload for frontend
- Redirect URI: `http://localhost:8000/api/auth/google/callback`

### Production (Server)

- HTTPS required
- Debug mode disabled
- Optimized builds
- Redirect URI: `https://yourdomain.com/api/auth/google/callback`
- Strong secrets
- Firewall enabled
- Monitoring configured

## 🔗 Useful Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild services
docker-compose build

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend

# Execute command in container
docker-compose exec backend python manage.py

# Scale celery workers
docker-compose up -d --scale celery-worker=3

# Export database
docker-compose exec postgres pg_dump -U madness_user madness_carlo > backup.sql

# Import database
docker-compose exec -T postgres psql -U madness_user madness_carlo < backup.sql

# Clean everything and start fresh
docker-compose down -v
docker-compose up -d --build
```

## 📞 Support and Maintenance

For ongoing maintenance:

1. **Weekly**: Check logs for errors
2. **Monthly**: Update Docker images
3. **Quarterly**: Review and update secrets
4. **Yearly**: Renew SSL certificates (auto with Let's Encrypt)

## 🚀 Advanced: Multi-Server Setup

For high-traffic deployments, consider:

- **Load Balancer**: Nginx/HAProxy across multiple app servers
- **Separate Database Server**: Dedicated PostgreSQL instance
- **Redis Cluster**: For better caching and job queue performance
- **CDN**: CloudFlare or similar for static assets
- **Container Orchestration**: Docker Swarm or Kubernetes

---

## Quick Reference: Production Deployment Checklist

```bash
# 1. Server setup
ssh user@server
git clone repo && cd repo
git checkout branch/web-app

# 2. Download AtomicCards.json
wget https://mtgjson.com/api/v5/AtomicCards.json

# 3. Configure .env
nano .env  # Add production values

# 4. Deploy
docker-compose up -d --build

# 5. Load config
docker-compose exec backend python load_default_config.py --force

# 6. Setup Nginx + SSL
sudo apt install nginx certbot python3-certbot-nginx
sudo nano /etc/nginx/sites-available/madnesscarlo
sudo certbot --nginx -d yourdomain.com

# 7. Monitor
docker-compose logs -f
```

Your app should now be live at `https://yourdomain.com`! 🎉

