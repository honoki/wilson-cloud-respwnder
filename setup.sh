#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: ./setup.sh <domainname>"
    exit 1
fi

DOMAIN_NAME=$1
PUBLIC_IP=$(curl -s ifconfig.io)

# TODO: only show this warning after we established the domain is not properly configured
# dig +short $DOMAIN_NAME soa | cut -d' ' -f1
echo "Make sure the name servers (NS records) for $DOMAIN_NAME point to $PUBLIC_IP before running this!\n"

echo "Generating settings.env..."
# Preserve TSIG key across re-runs so existing certs remain valid
TSIG_SECRET=$(grep "^TSIG_SECRET=" settings.env 2>/dev/null | cut -d'=' -f2-)
if [ -z "$TSIG_SECRET" ]; then
    TSIG_SECRET=$(openssl rand -base64 32)
fi
echo "SLACK_WEBHOOK=" > settings.env
echo "DISCORD_WEBHOOK=" >> settings.env
echo "DOMAIN=$DOMAIN_NAME" >> settings.env
echo "TSIG_SECRET=$TSIG_SECRET" >> settings.env

echo "Generating config files..."
sed "s/example.com/$DOMAIN_NAME/g" ./conf/caddy/Caddyfile.tpl > ./conf/caddy/Caddyfile
sed -e "s|example.com|$DOMAIN_NAME|g" -e "s|TSIG_SECRET_PLACEHOLDER|$TSIG_SECRET|g" ./conf/bind9/named.conf.local.tpl > ./conf/bind9/named.conf.local
sed -e "s/example.com/$DOMAIN_NAME/g;s/1.1.1.1/$PUBLIC_IP/g" ./dns/zonefile.db.tpl > ./dns/zonefile.db

echo "Setup complete. Add your webhooks in 'settings.env'. Run 'docker-compose up -d' to get started."
echo "Caddy will automatically obtain and renew TLS certificates on first startup."