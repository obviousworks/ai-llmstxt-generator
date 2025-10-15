#!/bin/bash
set -e

echo "=========================================="
echo "LLMs.txt Generator - Systemd Installation"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Configuration
INSTALL_DIR="/opt/llms-generator"
LOG_DIR="/var/log/llms-generator"
SERVICE_USER="www-data"

echo ""
echo "📋 Configuration:"
echo "   Install Directory: $INSTALL_DIR"
echo "   Log Directory: $LOG_DIR"
echo "   Service User: $SERVICE_USER"
echo ""

# Confirm installation
read -p "Continue with installation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$INSTALL_DIR/generated"
mkdir -p "$INSTALL_DIR/config"

# Copy application files
echo "📦 Copying application files..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Copy backend
cp -r "$SCRIPT_DIR/backend" "$INSTALL_DIR/"

# Copy frontend (build first if needed)
if [ ! -d "$SCRIPT_DIR/.next" ]; then
    echo "🔨 Building frontend..."
    cd "$SCRIPT_DIR"
    npm install
    npm run build
fi

cp -r "$SCRIPT_DIR/.next" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/public" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/package.json" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/package-lock.json" "$INSTALL_DIR/" 2>/dev/null || true

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd "$INSTALL_DIR/backend"
pip3 install -r requirements.txt

# Install Node dependencies
echo "📦 Installing Node dependencies..."
cd "$INSTALL_DIR"
npm ci --only=production

# Set permissions
echo "🔒 Setting permissions..."
chown -R $SERVICE_USER:$SERVICE_USER "$INSTALL_DIR"
chown -R $SERVICE_USER:$SERVICE_USER "$LOG_DIR"
chmod 755 "$INSTALL_DIR"
chmod 755 "$LOG_DIR"

# Install systemd service files
echo "⚙️  Installing systemd services..."
cp "$SCRIPT_DIR/systemd/llms-api.service" /etc/systemd/system/
cp "$SCRIPT_DIR/systemd/llms-frontend.service" /etc/systemd/system/

# Prompt for OpenAI API key
echo ""
echo "🔑 OpenAI API Key Configuration"
read -p "Enter your OpenAI API Key (or press Enter to configure later): " api_key

if [ ! -z "$api_key" ]; then
    sed -i "s/your_openai_api_key_here/$api_key/" /etc/systemd/system/llms-api.service
    echo "✅ API key configured"
else
    echo "⚠️  Remember to edit /etc/systemd/system/llms-api.service and add your API key"
fi

# Reload systemd
echo "🔄 Reloading systemd..."
systemctl daemon-reload

# Enable services
echo "✅ Enabling services..."
systemctl enable llms-api.service
systemctl enable llms-frontend.service

# Start services
echo "🚀 Starting services..."
systemctl start llms-api.service
sleep 3
systemctl start llms-frontend.service

# Check status
echo ""
echo "=========================================="
echo "📊 Service Status:"
echo "=========================================="
systemctl status llms-api.service --no-pager -l || true
echo ""
systemctl status llms-frontend.service --no-pager -l || true

echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "📍 Application installed at: $INSTALL_DIR"
echo "📝 Logs available at: $LOG_DIR"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status llms-api llms-frontend"
echo "   sudo systemctl restart llms-api llms-frontend"
echo "   sudo systemctl stop llms-api llms-frontend"
echo "   sudo journalctl -u llms-api -f"
echo "   sudo journalctl -u llms-frontend -f"
echo ""
echo "📚 Next steps:"
echo "   1. Configure automation: See scripts/ directory"
echo "   2. Setup Nginx: See nginx/ directory"
echo "   3. Configure websites: Edit config/websites.conf"
echo ""
