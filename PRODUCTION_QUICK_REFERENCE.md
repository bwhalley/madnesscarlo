# Production Quick Reference Card

Quick commands for managing your production deployment.

## 🚀 Initial Deployment

```bash
# On fresh Ubuntu 22.04 server (as root):
sudo bash server-setup.sh

# Then as regular user:
cd ~/apps
git clone https://github.com/bwhalley/madnesscarlo.git
cd madnesscarlo
cp env.production.template .env
nano .env  # Fill in your values
bash deploy-prod.sh
```

## 📊 Service Management

```bash
# Check service status
docker compose ps

# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f nginx
docker compose logs -f celery

# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend

# Stop all services
docker compose down

# Start all services
docker compose up -d
```

## 🔄 Updates & Maintenance

```bash
# Update to latest code
cd ~/apps/madnesscarlo
git pull origin main

# Rebuild and restart
docker compose build
docker compose up -d

# Run database migrations
docker compose exec backend alembic upgrade head

# Reload configuration
docker compose exec backend python load_default_config.py --force
```

## 🗄️ Database Operations

```bash
# Backup database
docker compose exec db pg_dump -U madness_user madness_carlo > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
docker compose exec -T db psql -U madness_user madness_carlo < backup_20251028_120000.sql

# Connect to database
docker compose exec db psql -U madness_user madness_carlo

# Check database size
docker compose exec db psql -U madness_user -d madness_carlo -c "SELECT pg_size_pretty(pg_database_size('madness_carlo'));"

# View recent simulations
docker compose exec db psql -U madness_user -d madness_carlo -c "SELECT id, status, runs, turns, created_at FROM simulations ORDER BY created_at DESC LIMIT 10;"
```

## 📜 SSL/Certificate Management

```bash
# Check certificate status
docker compose exec nginx certbot certificates

# Renew certificates manually
docker compose exec nginx certbot renew

# Reload nginx after renewal
docker compose exec nginx nginx -s reload

# Test nginx configuration
docker compose exec nginx nginx -t

# View SSL expiry
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

## 🔍 Monitoring & Debugging

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Monitor Docker resources
docker stats

# Check container health
docker compose ps

# View backend error logs
docker compose logs backend --tail 100 | grep ERROR

# View Celery worker status
docker compose logs celery --tail 50

# Check Redis
docker compose exec redis redis-cli PING

# View active simulations
docker compose exec backend python -c "from app.models.simulation import Simulation; from app.utils.database import SessionLocal; db = SessionLocal(); print([s.id for s in db.query(Simulation).filter(Simulation.status == 'running').all()])"
```

## 🧹 Cleanup & Optimization

```bash
# Remove unused Docker images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove stopped containers
docker container prune

# Full cleanup (careful!)
docker system prune -a --volumes

# Clean old logs
docker compose logs --tail 0 > /dev/null

# View Docker disk usage
docker system df
```

## 🌐 Networking & Firewall

```bash
# Check firewall status
sudo ufw status

# Open additional port
sudo ufw allow PORT/tcp

# Check listening ports
sudo netstat -tlnp

# Test connectivity
curl https://yourdomain.com/api/health

# Check DNS
nslookup yourdomain.com
dig yourdomain.com
```

## 📦 Environment Variables

```bash
# View current environment
docker compose exec backend env

# Update environment variables
nano .env
docker compose up -d  # Restart to apply

# Check specific variable
docker compose exec backend printenv DOMAIN
```

## 🚨 Troubleshooting

### Backend won't start

```bash
# Check logs
docker compose logs backend

# Check database connection
docker compose exec backend python -c "from app.utils.database import engine; engine.connect(); print('DB OK')"

# Restart with fresh build
docker compose down
docker compose build --no-cache backend
docker compose up -d
```

### SSL certificate errors

```bash
# Check certificate
docker compose exec nginx certbot certificates

# Re-run Let's Encrypt setup
./init-letsencrypt.sh

# Check nginx config
docker compose exec nginx nginx -t
```

### Can't access site

```bash
# Check DNS
ping yourdomain.com

# Check firewall
sudo ufw status

# Check nginx
docker compose logs nginx --tail 50

# Check if port is listening
sudo netstat -tlnp | grep :443
```

### Simulation not running

```bash
# Check Celery worker
docker compose logs celery --tail 50

# Check Redis
docker compose exec redis redis-cli PING

# Restart Celery
docker compose restart celery
```

## 📈 Performance Tuning

```bash
# Monitor resources
docker stats

# Check database performance
docker compose exec db psql -U madness_user -d madness_carlo -c "SELECT * FROM pg_stat_activity;"

# Vacuum database
docker compose exec db psql -U madness_user -d madness_carlo -c "VACUUM ANALYZE;"

# Check slow queries
docker compose logs backend | grep "slow query"
```

## 🔐 Security

```bash
# Update all packages
sudo apt update && sudo apt upgrade -y

# Check for security updates
sudo unattended-upgrades --dry-run

# Review firewall rules
sudo ufw status verbose

# Check for exposed ports
sudo netstat -tlnp

# Update Docker
curl -fsSL https://get.docker.com | sh
```

## 📱 Quick Health Checks

```bash
# One-liner health check
curl -s https://yourdomain.com/api/health | jq .

# Check all services
docker compose ps | grep -v "Up" || echo "All services running"

# Check disk space
df -h / | awk 'NR==2 {print "Disk usage: " $5}'

# Check memory
free -h | awk 'NR==2 {print "Memory usage: " $3 "/" $2}'

# Full system check
echo "=== System Status ===" && \
docker compose ps && \
echo "" && \
df -h / | tail -1 && \
free -h | grep Mem
```

## 🆘 Emergency Procedures

### Site is down

```bash
# Quick restart
docker compose restart

# Nuclear option (rebuild everything)
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Database corruption

```bash
# Restore from backup
docker compose down
docker compose up -d db
docker compose exec -T db psql -U madness_user madness_carlo < latest_backup.sql
docker compose up -d
```

### Out of disk space

```bash
# Clean Docker
docker system prune -a --volumes

# Find large files
du -h --max-depth=1 / | sort -hr | head -20

# Clean logs
truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

## 📞 Support

- **Logs**: Always check `docker compose logs` first
- **GitHub**: https://github.com/bwhalley/madnesscarlo
- **Documentation**: See `PRODUCTION_DEPLOYMENT_GUIDE.md`

## 💡 Pro Tips

1. **Regular backups**: Set up daily database backups
2. **Monitor logs**: Use `docker compose logs -f` in a tmux/screen session
3. **Health checks**: Add a cron job to check API health
4. **Resource monitoring**: Use `docker stats` to watch resource usage
5. **Update regularly**: Pull latest code and rebuild weekly

---

**Keep this file handy!** Bookmark it or print it for quick reference during operations.

