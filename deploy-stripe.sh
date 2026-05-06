#!/bin/bash

echo "🚀 Deploying Heathrow Black Cabs with Stripe..."

# Navigate to project directory
cd /var/www/heathrowblackcabs

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin master

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Update Nginx configuration
echo "⚙️  Updating Nginx configuration..."

# Backup existing config
cp /etc/nginx/sites-enabled/heathrowblackcabs /etc/nginx/sites-enabled/heathrowblackcabs.backup

# Check if /book location already exists
if ! grep -q "location /book" /etc/nginx/sites-enabled/heathrowblackcabs; then
    echo "Adding /book endpoint to Nginx..."
    
    # Find the server block and add the location before the closing brace
    sed -i '/server {/a\    location /book {\n        proxy_pass http://127.0.0.1:5005;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n    }\n' /etc/nginx/sites-enabled/heathrowblackcabs
fi

# Test Nginx configuration
echo "🧪 Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    echo "🔄 Reloading Nginx..."
    systemctl reload nginx
else
    echo "❌ Nginx configuration error! Restoring backup..."
    cp /etc/nginx/sites-enabled/heathrowblackcabs.backup /etc/nginx/sites-enabled/heathrowblackcabs
    exit 1
fi

# Restart the booking service
echo "🔄 Restarting heathrowblackcabs service..."
systemctl restart heathrowblackcabs

# Check service status
echo "📊 Checking service status..."
systemctl status heathrowblackcabs --no-pager

echo ""
echo "✅ Deployment complete!"
echo "🌐 Website: https://heathrowblackcabs.co.uk"
echo "💳 Stripe payments are now active"
echo ""
echo "📝 To view logs, run: sudo journalctl -u heathrowblackcabs -f"
