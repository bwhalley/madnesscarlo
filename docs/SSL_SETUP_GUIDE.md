# SSL/HTTPS Setup Guide with Let's Encrypt

Complete guide for setting up SSL certificates with Let's Encrypt for secure HTTPS connections.

---

## 🔐 Overview

This guide covers two SSL setup scenarios:
1. **Production**: Real Let's Encrypt certificates for your domain
2. **Development**: Self-signed certificates for local testing

---

## 📋 Prerequisites

### For Production SSL
- ✅ A registered domain name (e.g., `madness.yourdomain.com`)
- ✅ DNS A record pointing your domain to your server's IP address
- ✅ Ports 80 and 443 open on your server firewall
- ✅ Docker and docker-compose installed
- ✅ Email address for Let's Encrypt notifications

### For Development (Local)
- ✅ Docker and docker-compose installed
- ✅ No domain required (uses self-signed certificates)

---

## 🚀 Production Setup (Let's Encrypt)

### Step 1: Configure Environment Variables

Edit your `.env` file:

```bash
# Domain name (without http:// or https://)
DOMAIN=madness.yourdomain.com

# Your email for Let's Encrypt notifications
SSL_EMAIL=your-email@example.com

# Start with staging for testing (1), then use production (0)
SSL_STAGING=1
```

### Step 2: Verify DNS Configuration

Ensure your domain points to your server:

```bash
# Should return your server's IP address
dig +short madness.yourdomain.com

# Or use nslookup
nslookup madness.yourdomain.com
```

### Step 3: Start Services

Start all services (without SSL initially):

```bash
docker-compose up -d
```

### Step 4: Run Let's Encrypt Initialization

```bash
./init-letsencrypt.sh
```

This script will:
1. ✅ Download recommended TLS parameters
2. ✅ Create a temporary dummy certificate
3. ✅ Start nginx
4. ✅ Request a Let's Encrypt certificate
5. ✅ Reload nginx with the new certificate

**First time?** Use staging certificates (`SSL_STAGING=1`) to avoid hitting rate limits.

### Step 5: Update Nginx Configuration for SSL

Once you have certificates, update the nginx configuration:

```bash
# Copy the SSL configuration template
cp nginx/conf.d/ssl.conf.template nginx/conf.d/default.conf

# Replace ${DOMAIN} with your actual domain
sed -i "s/\${DOMAIN}/$DOMAIN/g" nginx/conf.d/default.conf

# Restart nginx
docker-compose restart nginx
```

### Step 6: Test with Staging Certificates

Visit your site at `https://madness.yourdomain.com`

You'll see a certificate warning (expected with staging certificates). This confirms:
- ✅ HTTPS is working
- ✅ Nginx SSL configuration is correct
- ✅ Let's Encrypt challenges are succeeding

### Step 7: Get Production Certificates

Once staging works, get production certificates:

```bash
# Stop the services
docker-compose down

# Update .env file
SSL_STAGING=0

# Re-run initialization for production certificates
./init-letsencrypt.sh

# Restart services
docker-compose up -d
```

Now visit `https://madness.yourdomain.com` - you should see a valid certificate!

---

## 🧪 Development Setup (Self-Signed Certificates)

For local development without a domain:

### Option 1: Skip SSL (Simplest)

Just use HTTP for local development:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

No configuration needed - it just works!

### Option 2: Self-Signed Certificates

If you need to test HTTPS locally:

```bash
# Create self-signed certificates
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/selfsigned.key \
  -out nginx/ssl/selfsigned.crt \
  -subj "/C=US/ST=State/L=City/O=Development/CN=localhost"

# Use the development nginx config
cp nginx/conf.d/dev-ssl.conf nginx/conf.d/default.conf

# Start services
docker-compose up -d nginx
```

Visit https://localhost - you'll see a certificate warning (expected with self-signed certs).

---

## 📝 nginx Configuration Files

### Current Configuration Options

```
nginx/conf.d/
├── default.conf              # Active configuration (edit this)
├── ssl.conf.template         # Production SSL template
└── dev-ssl.conf.template     # Development SSL template (create if needed)
```

### Switching Configurations

```bash
# Use HTTP only (initial setup)
# - Already configured in default.conf for initial certbot setup

# Use HTTPS with Let's Encrypt
cp nginx/conf.d/ssl.conf.template nginx/conf.d/default.conf
sed -i "s/\${DOMAIN}/$DOMAIN/g" nginx/conf.d/default.conf
docker-compose restart nginx

# Use HTTPS with self-signed certs (local dev)
# Create dev-ssl.conf with paths to self-signed certs
# Restart nginx
```

---

## 🔄 Certificate Renewal

Let's Encrypt certificates are valid for 90 days. The certbot container automatically renews them.

### Automatic Renewal

The `certbot` service in docker-compose.yml runs twice daily and renews certificates when they're within 30 days of expiration.

### Manual Renewal

To manually renew certificates:

```bash
# Renew certificates
docker-compose run --rm certbot renew

# Reload nginx
docker-compose exec nginx nginx -s reload
```

### Test Renewal Process

```bash
# Dry run - tests renewal without actually renewing
docker-compose run --rm certbot renew --dry-run
```

---

## 🔍 Troubleshooting

### Certificate Request Fails

**Problem**: `Failed to obtain certificate`

**Solutions**:
1. Verify DNS is configured correctly
   ```bash
   dig +short $DOMAIN
   ```

2. Check port 80 is accessible
   ```bash
   curl http://$DOMAIN/.well-known/acme-challenge/test
   ```

3. Check nginx logs
   ```bash
   docker-compose logs nginx
   ```

4. Check certbot logs
   ```bash
   docker-compose logs certbot
   ```

### "Too Many Requests" Error

**Problem**: Hit Let's Encrypt rate limit

**Solutions**:
- Use staging certificates for testing (`SSL_STAGING=1`)
- Wait a week for rate limit to reset
- See: https://letsencrypt.org/docs/rate-limits/

### nginx Fails to Start

**Problem**: `nginx: [emerg] cannot load certificate`

**Solutions**:
1. Ensure certificates exist:
   ```bash
   ls -la certbot/conf/live/$DOMAIN/
   ```

2. Check nginx configuration:
   ```bash
   docker-compose exec nginx nginx -t
   ```

3. Recreate certificates:
   ```bash
   ./init-letsencrypt.sh
   ```

### Browser Shows "Not Secure"

**Staging Certificates**:
- Expected! Staging certs are for testing only
- Use production certificates (`SSL_STAGING=0`)

**Self-Signed Certificates**:
- Expected! Browsers don't trust self-signed certs
- Click "Advanced" → "Proceed to site" for testing

**Production Certificates**:
- Check certificate expiration: `docker-compose run --rm certbot certificates`
- Ensure using correct domain in nginx config
- Clear browser cache

---

## 📊 Certificate Information

### View Certificate Details

```bash
# List all certificates
docker-compose run --rm certbot certificates

# Check certificate expiration
docker-compose exec nginx openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -noout -dates

# View full certificate details
docker-compose exec nginx openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -noout -text
```

---

## 🔒 Security Best Practices

### 1. Strong SSL Configuration

The provided `ssl.conf.template` includes:
- ✅ TLS 1.2 and 1.3 only
- ✅ Strong cipher suites
- ✅ SSL stapling
- ✅ Security headers (HSTS, X-Frame-Options, etc.)

### 2. HTTPS Redirect

After obtaining certificates, all HTTP traffic is redirected to HTTPS:

```nginx
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://$host$request_uri;
}
```

### 3. HSTS Header

Forces browsers to always use HTTPS:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 4. Regular Updates

```bash
# Update certbot image
docker-compose pull certbot

# Update nginx image
docker-compose pull nginx

# Restart services
docker-compose up -d
```

---

## 📁 File Structure

```
project/
├── nginx/
│   ├── conf.d/
│   │   ├── default.conf              # Active nginx config
│   │   └── ssl.conf.template         # SSL template
│   └── ssl/
│       ├── selfsigned.crt            # Self-signed cert (dev only)
│       └── selfsigned.key            # Self-signed key (dev only)
├── certbot/
│   ├── conf/                         # Let's Encrypt certificates
│   │   └── live/$DOMAIN/
│   │       ├── fullchain.pem         # Certificate chain
│   │       ├── privkey.pem           # Private key
│   │       └── ...
│   └── www/                          # ACME challenge files
├── init-letsencrypt.sh               # SSL setup script
└── docker-compose.yml                # Includes nginx & certbot
```

---

## 🎯 Quick Reference

### Common Commands

```bash
# Initial SSL setup
./init-letsencrypt.sh

# Manual certificate renewal
docker-compose run --rm certbot renew
docker-compose exec nginx nginx -s reload

# View certificates
docker-compose run --rm certbot certificates

# Test nginx configuration
docker-compose exec nginx nginx -t

# View nginx logs
docker-compose logs -f nginx

# View certbot logs
docker-compose logs certbot

# Restart nginx
docker-compose restart nginx

# Complete service restart
docker-compose down
docker-compose up -d
```

### URLs

- **Development**: http://localhost:5173 or https://localhost
- **Production**: https://madness.yourdomain.com

### Important Paths

- Certificates: `certbot/conf/live/$DOMAIN/`
- nginx config: `nginx/conf.d/default.conf`
- Init script: `init-letsencrypt.sh`

---

## 📚 Additional Resources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Let's Encrypt Rate Limits](https://letsencrypt.org/docs/rate-limits/)
- [Certbot Documentation](https://eff-certbot.readthedocs.io/)
- [nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)

---

## ✅ Post-Setup Checklist

After SSL setup:

- [ ] SSL certificates obtained successfully
- [ ] nginx configuration updated for HTTPS
- [ ] HTTP automatically redirects to HTTPS
- [ ] Browser shows valid certificate (production)
- [ ] WebSockets work over WSS
- [ ] Google OAuth redirect URI updated to HTTPS
- [ ] All API calls use HTTPS
- [ ] Certificate auto-renewal tested

---

**Need Help?** Check the troubleshooting section or review the docker-compose logs.

**Security Notice**: Never commit your actual `.env` file or certificates to git. The `.gitignore` file is configured to exclude them.

