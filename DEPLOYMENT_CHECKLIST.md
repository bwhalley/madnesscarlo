# 🚀 Production Deployment Checklist

Use this checklist when deploying to your production server.

## Pre-Deployment (On Your Local Machine)

- [ ] Code is committed and pushed to GitHub main branch
- [ ] All tests passing locally
- [ ] Documentation is up to date
- [ ] You have your Google OAuth credentials ready

## Domain Setup

- [ ] Domain name purchased/available (e.g., `madnesscarlo.yourdomain.com`)
- [ ] DNS A record created pointing to server IP
- [ ] DNS propagation verified (`nslookup madnesscarlo.yourdomain.com`)

## Server Preparation (SSH into server)

- [ ] Ubuntu 22.04 server accessible via SSH
- [ ] Server has public IP address
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker compose version`)
- [ ] Git installed (`git --version`)
- [ ] Firewall configured (ports 22, 80, 443 open)

```bash
# Quick server prep commands:
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo apt install -y git docker-compose-plugin ufw certbot
sudo ufw allow ssh && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw enable
```

## Application Setup

- [ ] Repository cloned (`git clone https://github.com/bwhalley/madnesscarlo.git`)
- [ ] `.env` file created with production values
- [ ] `POSTGRES_PASSWORD` set to secure random value
- [ ] `SECRET_KEY` set to secure random value
- [ ] `GOOGLE_CLIENT_ID` configured
- [ ] `GOOGLE_CLIENT_SECRET` configured
- [ ] `DOMAIN` set to your domain name
- [ ] `CERTBOT_EMAIL` set to your email
- [ ] `AtomicCards.json` downloaded to `backend/` directory

```bash
# Quick .env setup:
cd ~/apps/madnesscarlo
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)" >> .env
# Then edit with nano/vim to add other values
```

## Google OAuth Configuration

- [ ] Google Cloud Console project created
- [ ] OAuth 2.0 credentials created
- [ ] **Authorized JavaScript origins** includes `https://yourdomain.com`
- [ ] **Authorized redirect URIs** includes `https://yourdomain.com/auth/callback`
- [ ] Test users added (if in Testing mode)

## SSL/HTTPS Setup

- [ ] Domain is resolving to server IP
- [ ] `init-letsencrypt.sh` updated with your domain
- [ ] `init-letsencrypt.sh` updated with your email
- [ ] Nginx config updated with your domain
- [ ] Certbot directories created

```bash
# Verify domain resolves:
ping -c 3 yourdomain.com

# Update SSL script:
sed -i 's/example.com/yourdomain.com/g' init-letsencrypt.sh
sed -i 's/your-email@example.com/your-email@example.com/g' init-letsencrypt.sh
chmod +x init-letsencrypt.sh
```

## Build and Deploy

- [ ] SSL initialization script run successfully (`./init-letsencrypt.sh`)
- [ ] Docker images built (`docker compose build`)
- [ ] Services started (`docker compose up -d`)
- [ ] All containers running (`docker compose ps` shows all "Up")
- [ ] Database initialized (`alembic upgrade head`)
- [ ] Default config loaded (`python load_default_config.py --force`)

```bash
# Deploy commands:
cd ~/apps/madnesscarlo
./init-letsencrypt.sh
docker compose build
docker compose up -d
docker compose exec backend alembic upgrade head
docker compose exec backend python load_default_config.py --force
```

## Verification

- [ ] Site accessible at `https://yourdomain.com`
- [ ] Green padlock (valid SSL certificate)
- [ ] Login page loads
- [ ] Google OAuth login works
- [ ] Can create a deck
- [ ] Can create a configuration
- [ ] Can run a simulation
- [ ] Simulation completes successfully
- [ ] Can export to Google Sheets (if OAuth completed)

```bash
# Quick verification:
curl -I https://yourdomain.com  # Should return 200 OK
curl https://yourdomain.com/api/health  # Should return {"status":"healthy"}
```

## Post-Deployment

- [ ] SSL certificate auto-renewal configured (via certbot cron)
- [ ] Monitoring set up (optional)
- [ ] Backup strategy implemented
- [ ] Documentation updated with production URL
- [ ] Team notified of new deployment

## Common Issues Checklist

If something doesn't work:

- [ ] DNS is fully propagated (wait up to 1 hour)
- [ ] Firewall allows ports 80 and 443
- [ ] Docker containers are all running
- [ ] `.env` variables are correct (no quotes around values)
- [ ] OAuth redirect URIs match exactly (https, correct domain, /auth/callback)
- [ ] Nginx logs checked (`docker compose logs nginx`)
- [ ] Backend logs checked (`docker compose logs backend`)

## Emergency Rollback

If you need to rollback:

```bash
cd ~/apps/madnesscarlo
git log --oneline  # Find previous commit
git checkout PREVIOUS_COMMIT_HASH
docker compose build
docker compose up -d
```

## Success Criteria

✅ Site is live at `https://yourdomain.com`  
✅ HTTPS is working with valid certificate  
✅ Users can log in with Google OAuth  
✅ All features work (decks, configs, simulations)  
✅ No errors in logs  
✅ Performance is acceptable  

---

**Time Estimate**: 30-60 minutes for full deployment (excluding DNS propagation wait time)

**Need Help?** Check `PRODUCTION_DEPLOYMENT_GUIDE.md` for detailed instructions.

