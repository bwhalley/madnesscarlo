#!/bin/bash
# Create self-signed SSL certificate for local development

set -e

echo "🔒 Creating self-signed SSL certificate for local development"
echo ""

# Create nginx/ssl directory if it doesn't exist
mkdir -p nginx/ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/selfsigned.key \
  -out nginx/ssl/selfsigned.crt \
  -subj "/C=US/ST=Local/L=Local/O=Development/CN=localhost"

echo "✅ Self-signed certificate created!"
echo ""
echo "Files created:"
echo "  - nginx/ssl/selfsigned.key"
echo "  - nginx/ssl/selfsigned.crt"
echo ""
echo "⚠️  Note: Your browser will show a security warning"
echo "    This is expected with self-signed certificates."
echo "    Click 'Advanced' → 'Proceed to localhost' to continue."
echo ""
echo "Next steps:"
echo "1. Update nginx/conf.d/default.conf to use these certificates"
echo "2. Start nginx: docker-compose up -d nginx"
echo "3. Access at: https://localhost"

