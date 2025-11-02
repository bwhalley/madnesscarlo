#!/bin/bash

# Initialize Let's Encrypt SSL certificates
# Based on: https://github.com/wmnnd/nginx-certbot

set -e

# Configuration
DOMAIN="${DOMAIN:-localhost}"
EMAIL="${SSL_EMAIL:-}"
STAGING="${SSL_STAGING:-1}"  # Set to 0 for production certificates
DATA_PATH="./certbot"
COMPOSE_FILE="docker-compose.yml"

echo "=== Let's Encrypt SSL Certificate Setup ==="
echo "Domain: $DOMAIN"
echo "Email: ${EMAIL:-Not provided}"
echo "Staging mode: $STAGING (0=production, 1=staging)"
echo ""
echo "⚠️  IMPORTANT: Let's Encrypt requires port 80 to be accessible for domain verification."
echo "   If you have another service (like Pi-hole) on port 80, temporarily stop it:"
echo "   sudo systemctl stop pihole-FTL  # or docker stop pihole"
echo "   You can restart it after certificates are obtained."
echo ""

# Validate inputs
if [ "$DOMAIN" = "localhost" ]; then
  echo "⚠️  WARNING: Domain is set to 'localhost'"
  echo "   Let's Encrypt certificates require a real domain name."
  echo "   For local development, use self-signed certificates instead."
  echo ""
  read -p "Continue anyway? (y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

if [ -z "$EMAIL" ]; then
  echo "❌ ERROR: SSL_EMAIL environment variable is required"
  echo "   Set it in your .env file or export it:"
  echo "   export SSL_EMAIL=your-email@example.com"
  exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
  echo "❌ ERROR: docker-compose is not installed"
  exit 1
fi

# Create directories if they don't exist
mkdir -p "$DATA_PATH/conf"
mkdir -p "$DATA_PATH/www"

# Download recommended TLS parameters if they don't exist
if [ ! -e "$DATA_PATH/conf/options-ssl-nginx.conf" ] || [ ! -e "$DATA_PATH/conf/ssl-dhparams.pem" ]; then
  echo "📥 Downloading recommended TLS parameters..."
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$DATA_PATH/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$DATA_PATH/conf/ssl-dhparams.pem"
  echo "✅ TLS parameters downloaded"
fi

# Check if certificates already exist
if [ -d "$DATA_PATH/conf/live/$DOMAIN" ]; then
  echo ""
  read -p "⚠️  Existing certificates found for $DOMAIN. Replace them? (y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Keeping existing certificates."
    exit 0
  fi
  echo "🗑️  Removing existing certificates..."
  docker-compose -f "$COMPOSE_FILE" run --rm --entrypoint "\
    rm -rf /etc/letsencrypt/live/$DOMAIN && \
    rm -rf /etc/letsencrypt/archive/$DOMAIN && \
    rm -rf /etc/letsencrypt/renewal/$DOMAIN.conf" certbot
fi

echo ""
echo "📝 Creating dummy certificate for $DOMAIN..."
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
docker-compose -f "$COMPOSE_FILE" run --rm --entrypoint "sh" certbot -c "\
  mkdir -p $CERT_PATH && \
  openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
    -keyout $CERT_PATH/privkey.pem \
    -out $CERT_PATH/fullchain.pem \
    -subj '/CN=localhost'" || {
  echo "❌ Failed to create dummy certificate"
  exit 1
}
echo "✅ Dummy certificate created"

echo ""
echo "🚀 Starting nginx..."
docker-compose -f "$COMPOSE_FILE" up -d nginx || {
  echo "❌ Failed to start nginx"
  exit 1
}
echo "✅ Nginx started"

echo ""
echo "🗑️  Deleting dummy certificate for $DOMAIN..."
docker-compose -f "$COMPOSE_FILE" run --rm --entrypoint "\
  rm -rf /etc/letsencrypt/live/$DOMAIN && \
  rm -rf /etc/letsencrypt/archive/$DOMAIN && \
  rm -rf /etc/letsencrypt/renewal/$DOMAIN.conf" certbot
echo "✅ Dummy certificate deleted"

echo ""
echo "📜 Requesting Let's Encrypt certificate for $DOMAIN..."

# Set certbot staging flag
STAGING_ARG=""
if [ "$STAGING" = "1" ]; then
  STAGING_ARG="--staging"
  echo "ℹ️  Using Let's Encrypt staging environment (test certificates)"
else
  echo "⚠️  Using Let's Encrypt PRODUCTION environment"
  echo "   Rate limits apply: https://letsencrypt.org/docs/rate-limits/"
fi

# Request certificate
docker-compose -f "$COMPOSE_FILE" run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $STAGING_ARG \
    --email $EMAIL \
    -d $DOMAIN \
    --rsa-key-size 4096 \
    --agree-tos \
    --force-renewal \
    --non-interactive" certbot || {
  echo "❌ Failed to obtain certificate"
  exit 1
}

echo ""
echo "✅ Certificate obtained successfully!"
echo ""
echo "🔄 Reloading nginx configuration..."
docker-compose -f "$COMPOSE_FILE" exec nginx nginx -s reload || {
  echo "⚠️  Failed to reload nginx. Restarting..."
  docker-compose -f "$COMPOSE_FILE" restart nginx
}

echo ""
echo "=========================================="
echo "✅ SSL Certificate Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update nginx/conf.d/default.conf with SSL configuration"
echo "   (Use nginx/conf.d/ssl.conf.template as a reference)"
echo "2. Restart nginx: docker-compose restart nginx"
echo "3. Test your site: https://$DOMAIN"
echo ""
if [ "$STAGING" = "1" ]; then
  echo "⚠️  You used staging certificates (for testing only)"
  echo "   To get production certificates, run:"
  echo "   SSL_STAGING=0 ./init-letsencrypt.sh"
  echo ""
fi
echo "Certificate renewal is handled automatically by certbot."
echo "Manual renewal: docker-compose run --rm certbot renew"
echo ""

