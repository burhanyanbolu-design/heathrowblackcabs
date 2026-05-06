#!/bin/bash
# Run this script on the server to create the .env file

echo "📝 Creating .env file for Heathrow Black Cabs..."

cat > /var/www/heathrowblackcabs/.env << 'EOF'
IONOS_USER=info@heathrowblackcabs.co.uk
IONOS_PASS=Yanbolu1973@
STRIPE_SECRET_KEY=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
EOF

chmod 600 /var/www/heathrowblackcabs/.env

echo "✅ .env file created successfully!"
echo "🔒 File permissions set to 600 (owner read/write only)"
