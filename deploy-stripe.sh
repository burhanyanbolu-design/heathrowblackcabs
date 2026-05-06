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

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 .env file not found!"
    echo "❌ Please create /var/www/heathrowblackcabs/.env with your credentials"
    echo ""
    echo "Example .env file:"
    echo "IONOS_USER=info@heathrowblackcabs.co.uk"
    echo "IONOS_PASS=your_password"
    echo "STRIPE_SECRET_KEY=sk_live_your_key"
    echo ""
    exit 1
fi

# Update systemd service to load environment variables
echo "⚙️  Updating systemd service..."
cat > /etc/systemd/system/heathrowblackcabs.service << 'SERVICEEOF'
[Unit]
Description=Heathrow Black Cabs Booking Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/var/www/heathrowblackcabs
EnvironmentFile=/var/www/heathrowblackcabs/.env
ExecStart=/usr/bin/python3 /var/www/heathrowblackcabs/booking_server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Reload systemd
systemctl daemon-reload

# Update Nginx configuration
echo "⚙️  Updating Nginx configuration..."

# Backup existing config
cp /etc/nginx/sites-enabled/heathrowblackcabs /etc/nginx/sites-enabled/heathrowblackcabs.backup 2>/dev/null || true

# Check if /book location already exists
if ! grep -q "location /book" /etc/nginx/sites-enabled/heathrowblackcabs 2>/dev/null; then
    echo "Adding /book endpoint to Nginx..."
    
    # Create new config
    cat > /etc/nginx/sites-available/heathrowblackcabs << 'NGINXEOF'
server {
    listen 80;
    server_name heathrowblackcabs.co.uk www.heathrowblackcabs.co.uk;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name heathrowblackcabs.co.uk www.heathrowblackcabs.co.uk;

    ssl_certificate /etc/letsencrypt/live/heathrowblackcabs.co.uk/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/heathrowblackcabs.co.uk/privkey.pem;

    root /var/www/heathrowblackcabs;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /book {
        proxy_pass http://127.0.0.1:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    access_log /var/log/nginx/heathrowblackcabs_access.log;
    error_log /var/log/nginx/heathrowblackcabs_error.log;
}
NGINXEOF

    ln -sf /etc/nginx/sites-available/heathrowblackcabs /etc/nginx/sites-enabled/heathrowblackcabs
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
    cp /etc/nginx/sites-enabled/heathrowblackcabs.backup /etc/nginx/sites-enabled/heathrowblackcabs 2>/dev/null || true
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
