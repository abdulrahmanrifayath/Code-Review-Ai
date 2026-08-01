#!/usr/bin/env bash
# Automated Let's Encrypt SSL Certificate Setup Script for ReviewAI
set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <domain-name> <email-address>"
    echo "Example: $0 reviewai.yourdomain.com admin@yourdomain.com"
    exit 1
fi

DOMAIN=$1
EMAIL=$2
RSA_KEY_SIZE=4096
DATA_PATH="./certbot"
STAGING=0 # Set to 1 for testing to avoid hitting request limits

if [ -d "$DATA_PATH" ]; then
    read -p "Existing data found for $DOMAIN. Continue and replace? (y/N) " decision
    if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
        exit
    fi
fi

echo "### Creating dummy certificate for $DOMAIN..."
path="/etc/letsencrypt/live/$DOMAIN"
mkdir -p "$DATA_PATH/conf/live/$DOMAIN"
docker compose -f docker-compose.prod.yml run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:2048 -days 1\
    -keyout '$path/privkey.pem' \
    -out '$path/fullchain.pem' \
    -subj '/CN=localhost'" nginx

echo "### Starting NGINX container..."
docker compose -f docker-compose.prod.yml up --force-recreate -d nginx

echo "### Deleting dummy certificate for $DOMAIN..."
docker compose -f docker-compose.prod.yml run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$DOMAIN && \
  rm -Rf /etc/letsencrypt/archive/$DOMAIN && \
  rm -Rf /etc/letsencrypt/renewal/$DOMAIN.conf" nginx

echo "### Requesting Let's Encrypt certificate for $DOMAIN..."
domain_args="-d $DOMAIN"

case "$STAGING" in
  0) staging_arg="" ;;
  *) staging_arg="--staging" ;;
esac

docker compose -f docker-compose.prod.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $domain_args \
    --email $EMAIL \
    --rsa-key-size $RSA_KEY_SIZE \
    --agree-tos \
    --force-renewal" nginx

echo "### Reloading NGINX..."
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
echo "=== SSL Setup Completed for $DOMAIN ==="
