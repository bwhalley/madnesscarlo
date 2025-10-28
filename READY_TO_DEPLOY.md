# 🚀 Ready to Deploy - Production Deployment Summary

**Status**: ✅ All deployment tools and documentation ready  
**Target**: Ubuntu 22.04 server  
**Deployment Method**: Automated with Docker Compose + SSL  
**Date**: October 28, 2025

---

## ✅ What's Been Prepared

Everything you need to deploy MTG Madness Carlo Simulator to production:

### 📚 Documentation
1. **PRODUCTION_DEPLOYMENT_GUIDE.md** - Complete step-by-step guide (10 parts)
2. **DEPLOYMENT_CHECKLIST.md** - Quick checklist for deployment
3. **PRODUCTION_QUICK_REFERENCE.md** - Command reference for operations
4. **CONFIG_MANAGEMENT_MERGED.md** - Recent feature summary

### 🛠️ Automation Scripts
1. **server-setup.sh** - Initial server setup (run once)
2. **deploy-prod.sh** - Automated deployment (main deployment script)
3. **init-letsencrypt.sh** - SSL certificate setup (already exists)
4. **env.production.template** - Environment variables template

### 🏗️ Infrastructure
1. **Docker Compose** - Multi-container orchestration
2. **Nginx** - Reverse proxy with SSL
3. **PostgreSQL** - Database with backups
4. **Redis + Celery** - Background job processing
5. **Let's Encrypt** - Free SSL certificates (auto-renewing)

---

## 🎯 Your Deployment Path

### Step 1: Prepare Your Domain (5 minutes)

**What you need**:
- A domain name (e.g., `madnesscarlo.yourdomain.com`)
- Access to your domain's DNS settings

**What to do**:
1. Go to your domain registrar (GoDaddy, Namecheap, Cloudflare, etc.)
2. Add an A record:
   - **Name**: `madnesscarlo` (or `@` for root domain)
   - **Type**: A
   - **Value**: Your server's public IP address
   - **TTL**: 3600 or automatic
3. Wait 5-30 minutes for DNS propagation
4. Verify: `nslookup madnesscarlo.yourdomain.com` (should show your IP)

### Step 2: Initial Server Setup (10 minutes)

**Connect to your server**:
```bash
ssh your-username@YOUR_SERVER_IP
```

**Run the automated server setup**:
```bash
# Download and run server setup script
wget https://raw.githubusercontent.com/bwhalley/madnesscarlo/main/server-setup.sh
sudo bash server-setup.sh
```

**What it does**:
- ✅ Updates system packages
- ✅ Installs Docker & Docker Compose
- ✅ Installs Git and tools
- ✅ Configures firewall (ports 22, 80, 443)
- ✅ Sets up user permissions

**Then log out and log back in** (for Docker group to take effect):
```bash
exit
ssh your-username@YOUR_SERVER_IP
```

### Step 3: Clone and Configure (5 minutes)

```bash
# Create app directory and clone
mkdir -p ~/apps
cd ~/apps
git clone https://github.com/bwhalley/madnesscarlo.git
cd madnesscarlo

# Create .env file from template
cp env.production.template .env

# Edit with your values
nano .env
```

**Required values in .env**:
- `DOMAIN` - Your domain (e.g., madnesscarlo.yourdomain.com)
- `GOOGLE_CLIENT_ID` - From Google Cloud Console
- `GOOGLE_CLIENT_SECRET` - From Google Cloud Console
- `CERTBOT_EMAIL` - Your email for SSL notifications
- `POSTGRES_PASSWORD` - Will be auto-generated or set manually
- `SECRET_KEY` - Will be auto-generated or set manually

**Generate secure passwords**:
```bash
# These commands will output secure random values
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)"
echo "SECRET_KEY=$(openssl rand -hex 32)"
```

### Step 4: Update Google OAuth (5 minutes)

**⚠️ CRITICAL**: Update your OAuth settings in Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID
3. Add to **Authorized JavaScript origins**:
   ```
   https://madnesscarlo.yourdomain.com
   ```
4. Add to **Authorized redirect URIs**:
   ```
   https://madnesscarlo.yourdomain.com/auth/callback
   ```
5. Click **Save**

### Step 5: Deploy! (10 minutes)

```bash
# Still in ~/apps/madnesscarlo directory
bash deploy-prod.sh
```

**What it does**:
- ✅ Validates your .env file
- ✅ Downloads AtomicCards.json (large file)
- ✅ Sets up SSL certificates with Let's Encrypt
- ✅ Builds Docker images
- ✅ Starts all services
- ✅ Runs database migrations
- ✅ Loads default configuration
- ✅ Verifies deployment

**Wait for it to complete** (about 5-10 minutes)

### Step 6: Verify (2 minutes)

**Open your browser**:
```
https://madnesscarlo.yourdomain.com
```

**You should see**:
- ✅ Green padlock (secure HTTPS)
- ✅ Login page
- ✅ Google OAuth button

**Test the app**:
1. Click "Sign in with Google"
2. Log in with your Google account
3. Create a test deck
4. Create or duplicate a configuration
5. Run a simulation
6. Verify results appear

---

## 📋 Quick Deployment Commands

If you want to do it **manually** step-by-step:

```bash
# 1. Connect to server
ssh user@YOUR_SERVER_IP

# 2. Setup server (one time)
wget https://raw.githubusercontent.com/bwhalley/madnesscarlo/main/server-setup.sh
sudo bash server-setup.sh
exit  # Log out and back in

# 3. Clone repo
mkdir -p ~/apps && cd ~/apps
git clone https://github.com/bwhalley/madnesscarlo.git
cd madnesscarlo

# 4. Configure
cp env.production.template .env
nano .env  # Fill in your values

# 5. Deploy
bash deploy-prod.sh

# 6. Access
# Open https://your-domain.com in browser
```

---

## 🆘 If Something Goes Wrong

### DNS not resolving
```bash
# Check DNS
nslookup your-domain.com
# Wait 5-30 minutes for propagation
```

### SSL certificate failed
```bash
# Re-run SSL setup
cd ~/apps/madnesscarlo
./init-letsencrypt.sh
```

### Service not starting
```bash
# Check logs
cd ~/apps/madnesscarlo
docker compose logs backend
docker compose logs nginx

# Restart
docker compose restart
```

### Can't log in with Google
1. Verify OAuth redirect URIs in Google Cloud Console
2. Check .env has correct `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
3. Restart backend: `docker compose restart backend`

### Still stuck?
- Check **PRODUCTION_DEPLOYMENT_GUIDE.md** Part 8: Troubleshooting
- Check **PRODUCTION_QUICK_REFERENCE.md** for commands
- Review logs: `docker compose logs -f`

---

## 📊 After Deployment

### Daily Operations

**View status**:
```bash
cd ~/apps/madnesscarlo
docker compose ps
```

**View logs**:
```bash
docker compose logs -f backend
```

**Restart services**:
```bash
docker compose restart
```

### Updates

**Update to latest version**:
```bash
cd ~/apps/madnesscarlo
git pull origin main
docker compose build
docker compose up -d
```

### Backups

**Backup database**:
```bash
docker compose exec db pg_dump -U madness_user madness_carlo > backup_$(date +%Y%m%d).sql
```

---

## 🎯 Success Checklist

After deployment, verify:

- [ ] Site accessible at `https://your-domain.com`
- [ ] Green padlock (valid SSL certificate)
- [ ] Can log in with Google OAuth
- [ ] Can create decks
- [ ] Can create/edit configurations
- [ ] Can run simulations
- [ ] Simulations complete successfully
- [ ] Can view results
- [ ] Can export to Google Sheets (if OAuth completed)
- [ ] All tabs work (Decks, Configurations, Run Simulation, Simulations)

---

## 🚀 Estimated Timeline

| Task | Time | Difficulty |
|------|------|------------|
| Domain DNS setup | 5 min + wait | Easy |
| Server setup | 10 min | Easy |
| App configuration | 5 min | Easy |
| Google OAuth update | 5 min | Easy |
| Deployment | 10 min | Easy |
| Verification | 2 min | Easy |
| **Total Active Time** | **~40 min** | **Easy** |

*Plus DNS propagation wait (5-30 minutes)*

---

## 💡 Pro Tips

1. **Test locally first**: Make sure everything works on your local machine
2. **DNS wait time**: Set up DNS early, then work on server while it propagates
3. **Keep .env secure**: Never commit your .env file with real credentials
4. **Bookmark quick reference**: Keep `PRODUCTION_QUICK_REFERENCE.md` handy
5. **Set up backups**: Add a daily backup cron job
6. **Monitor resources**: Use `docker stats` to watch resource usage
7. **Update regularly**: Pull latest code weekly

---

## 📞 Support Resources

- **Full Guide**: `PRODUCTION_DEPLOYMENT_GUIDE.md`
- **Checklist**: `DEPLOYMENT_CHECKLIST.md`
- **Quick Reference**: `PRODUCTION_QUICK_REFERENCE.md`
- **GitHub**: https://github.com/bwhalley/madnesscarlo

---

## 🎉 Ready to Deploy!

You have everything you need:
- ✅ Comprehensive documentation
- ✅ Automated setup scripts
- ✅ SSL/HTTPS configuration
- ✅ Google OAuth integration
- ✅ Database management
- ✅ Troubleshooting guides

**Next step**: SSH into your server and run `server-setup.sh`!

Good luck! 🚀

