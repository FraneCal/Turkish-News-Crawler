#!/bin/bash

echo "🚀 Deploying News Crawler Web Application..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Install and configure Nginx
echo "🌐 Installing and configuring Nginx..."
apt update
apt install -y nginx

# Copy nginx configuration
cp nginx_config.conf /etc/nginx/sites-available/news-crawler
ln -sf /etc/nginx/sites-available/news-crawler /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

# Install and configure systemd service
echo "⚙️ Configuring systemd service..."
cp news-crawler.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable news-crawler.service

# Start services
echo "🔄 Starting services..."
systemctl start news-crawler.service
systemctl restart nginx

# Check status
echo "📊 Checking service status..."
systemctl status news-crawler.service --no-pager
systemctl status nginx --no-pager

echo "✅ Deployment complete!"
echo "🌍 Your web application should be accessible at:"
echo "   http://72.60.182.36"
echo "   or"
echo "   http://$(curl -s -4 ifconfig.me)"
echo ""
echo "📋 Useful commands:"
echo "   sudo systemctl status news-crawler.service"
echo "   sudo systemctl restart news-crawler.service"
echo "   sudo systemctl logs news-crawler.service"
echo "   sudo nginx -t"
echo "   sudo systemctl restart nginx"
