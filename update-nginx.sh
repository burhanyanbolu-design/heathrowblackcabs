#!/bin/bash

echo "⚙️  Updating Nginx for Heathrow Black Cabs..."

# Create a complete Nginx configuration
cat > /etc/nginx/sites-available/heathrowblackcabs << 'EOF'
server {
    listen 80;
    server_name heathrowblackcabs.co.uk www.heathrowblackcabs.co.uk;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name heathrowblackcabs.co.uk www.heathrowblackcabs.co.uk;

    # SSL certificates (adjust paths if needed)
    ssl_certificate /etc/letsencrypt/live/heathrowblackcabs.co.uk/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/heathrowblackcabs.co.uk/privkey.pem;

    # Root directory for static files
    root /var/www/heathrowblackcabs;
    index index.html;

    # Static files
    location / {
        try_files $uri $uri/ =404;
    }

    # Booking API endpoints
    location /book {
        proxy_pass http://127.0.0.1:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Logs
    access_log /var/log/nginx/heathrowblackcabs_access.log;
    error_log /var/log/nginx/heathrowblackcabs_error.log;
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/heathrowblackcabs /etc/nginx/sites-enabled/heathrowblackcabs

# Test configuration
echo "🧪 Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    echo "🔄 Reloading Nginx..."
    systemctl reload nginx
    echo "✅ Nginx updated successfully!"
else
    echo "❌ Nginx configuration error!"
    exit 1
fi
EOF
