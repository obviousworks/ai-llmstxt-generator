#!/bin/bash
# LLMs.txt Generator - Nginx Installation Script

set -e

echo "=========================================="
echo "LLMs.txt Generator - Nginx Setup"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "📦 Nginx not found. Installing..."
    apt update
    apt install -y nginx
fi

echo ""
echo "📋 Configuration:"
read -p "Enter your domain name (e.g., llms-generator.example.com): " domain

if [ -z "$domain" ]; then
    echo "❌ Domain name is required"
    exit 1
fi

echo ""
echo "Domain: $domain"
read -p "Continue with installation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Copy and customize config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="/etc/nginx/sites-available/llms-generator"

echo "📝 Creating nginx configuration..."
cp "$SCRIPT_DIR/llms-generator.conf" "$CONFIG_FILE"

# Replace domain placeholder
sed -i "s/your-domain.com/$domain/g" "$CONFIG_FILE"

echo "✅ Configuration created: $CONFIG_FILE"

# Create symlink
echo "🔗 Enabling site..."
ln -sf "$CONFIG_FILE" /etc/nginx/sites-enabled/llms-generator

# Test configuration
echo "🧪 Testing nginx configuration..."
if nginx -t; then
    echo "✅ Configuration is valid"
else
    echo "❌ Configuration test failed"
    exit 1
fi

# Reload nginx
echo "🔄 Reloading nginx..."
systemctl reload nginx

echo ""
echo "=========================================="
echo "✅ Nginx Configuration Installed!"
echo "=========================================="
echo ""
echo "📍 Configuration file: $CONFIG_FILE"
echo "🌐 Domain: $domain"
echo ""
echo "⚠️  Important: SSL is configured but certificates are not installed yet!"
echo ""
echo "🔒 To enable HTTPS with Let's Encrypt:"
echo "   1. Install certbot:"
echo "      sudo apt install certbot python3-certbot-nginx"
echo ""
echo "   2. Get SSL certificate:"
echo "      sudo certbot --nginx -d $domain"
echo ""
echo "   3. Test auto-renewal:"
echo "      sudo certbot renew --dry-run"
echo ""
echo "📝 For now, you can access via HTTP:"
echo "   http://$domain"
echo ""
echo "🔧 Useful commands:"
echo "   sudo nginx -t                    # Test configuration"
echo "   sudo systemctl reload nginx      # Reload nginx"
echo "   sudo systemctl status nginx      # Check status"
echo "   sudo tail -f /var/log/nginx/llms-generator-access.log"
echo ""
