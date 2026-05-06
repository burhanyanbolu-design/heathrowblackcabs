#!/bin/bash

echo "🔧 Fixing Stripe payment integration..."

# Update Nginx configuration
echo "⚙️  Updating Nginx configuration..."
cat > /etc/nginx/sites-available/heathrowblackcabs << 'EOF'
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

    location /create-payment-intent {
        proxy_pass http://127.0.0.1:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    access_log /var/log/nginx/heathrowblackcabs_access.log;
    error_log /var/log/nginx/heathrowblackcabs_error.log;
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/heathrowblackcabs /etc/nginx/sites-enabled/heathrowblackcabs

# Test Nginx
echo "🧪 Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    echo "🔄 Reloading Nginx..."
    systemctl reload nginx
    echo "✅ Nginx reloaded successfully!"
else
    echo "❌ Nginx configuration error!"
    exit 1
fi

# Pull latest code
echo "📥 Pulling latest code..."
cd /var/www/heathrowblackcabs
git pull origin master

echo ""
echo "✅ All done!"
echo "🌐 Test Stripe payment at: https://heathrowblackcabs.co.uk"
echo ""
