# ⚙️ Systemd Setup Guide

Run LLMs.txt Generator as system services on Linux with automatic startup and monitoring.

## 🚀 Quick Start

### Automated Installation

```bash
# Clone repository
git clone https://github.com/obviousworks/ai-llmstxt-generator.git
cd ai-llmstxt-generator/llm_txt_creator

# Run installation script
sudo ./systemd/install.sh
```

The script will:
1. ✅ Install to `/opt/llms-generator`
2. ✅ Create log directory `/var/log/llms-generator`
3. ✅ Install Python & Node dependencies
4. ✅ Configure systemd services
5. ✅ Start services automatically

---

## 📋 Manual Installation

### 1. Prerequisites

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip nodejs npm

# Verify installations
python3 --version
node --version
npm --version
```

### 2. Install Application

```bash
# Create installation directory
sudo mkdir -p /opt/llms-generator
sudo mkdir -p /var/log/llms-generator

# Copy application files
sudo cp -r backend /opt/llms-generator/
sudo cp -r .next /opt/llms-generator/
sudo cp -r public /opt/llms-generator/
sudo cp package*.json /opt/llms-generator/

# Install dependencies
cd /opt/llms-generator/backend
sudo pip3 install -r requirements.txt

cd /opt/llms-generator
sudo npm ci --only=production

# Set permissions
sudo chown -R www-data:www-data /opt/llms-generator
sudo chown -R www-data:www-data /var/log/llms-generator
```

### 3. Configure Services

```bash
# Copy service files
sudo cp systemd/llms-api.service /etc/systemd/system/
sudo cp systemd/llms-frontend.service /etc/systemd/system/

# Edit API service to add your OpenAI key
sudo nano /etc/systemd/system/llms-api.service
# Change: Environment="OPENAI_API_KEY=your_openai_api_key_here"
```

### 4. Enable & Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services (start on boot)
sudo systemctl enable llms-api.service
sudo systemctl enable llms-frontend.service

# Start services
sudo systemctl start llms-api.service
sudo systemctl start llms-frontend.service

# Check status
sudo systemctl status llms-api llms-frontend
```

---

## 🔧 Service Management

### Basic Commands

```bash
# Start services
sudo systemctl start llms-api llms-frontend

# Stop services
sudo systemctl stop llms-api llms-frontend

# Restart services
sudo systemctl restart llms-api llms-frontend

# Check status
sudo systemctl status llms-api llms-frontend

# Enable auto-start on boot
sudo systemctl enable llms-api llms-frontend

# Disable auto-start
sudo systemctl disable llms-api llms-frontend
```

### View Logs

```bash
# Real-time logs
sudo journalctl -u llms-api -f
sudo journalctl -u llms-frontend -f

# Last 100 lines
sudo journalctl -u llms-api -n 100
sudo journalctl -u llms-frontend -n 100

# Logs since today
sudo journalctl -u llms-api --since today

# Log files
tail -f /var/log/llms-generator/api.log
tail -f /var/log/llms-generator/frontend.log
```

---

## 🔒 Security Configuration

### Service User

Services run as `www-data` user for security. To use a different user:

```bash
# Create dedicated user
sudo useradd -r -s /bin/false llms-generator

# Update service files
sudo sed -i 's/www-data/llms-generator/g' /etc/systemd/system/llms-*.service

# Update permissions
sudo chown -R llms-generator:llms-generator /opt/llms-generator
sudo chown -R llms-generator:llms-generator /var/log/llms-generator

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart llms-api llms-frontend
```

### Environment Variables

Edit service files to add environment variables:

```bash
sudo nano /etc/systemd/system/llms-api.service
```

Add under `[Service]`:
```ini
Environment="OPENAI_API_KEY=your_key_here"
Environment="CUSTOM_VAR=value"
```

Or use an environment file:

```bash
# Create env file
sudo nano /opt/llms-generator/.env

# Add to service file
EnvironmentFile=/opt/llms-generator/.env
```

---

## 🌐 Nginx Integration

### Install Nginx

```bash
sudo apt install nginx
```

### Configure Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/llms-generator
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/llms-generator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check service status
sudo systemctl status llms-api llms-frontend

# Check logs for errors
sudo journalctl -u llms-api -n 50
sudo journalctl -u llms-frontend -n 50

# Verify permissions
ls -la /opt/llms-generator
ls -la /var/log/llms-generator

# Test manually
cd /opt/llms-generator/backend
python3 run_dev.py
```

### Port Already in Use

```bash
# Check what's using the ports
sudo lsof -i :8000
sudo lsof -i :3000

# Kill process if needed
sudo kill -9 <PID>

# Or change ports in service files
sudo nano /etc/systemd/system/llms-api.service
# Add: Environment="PORT=8001"
```

### Permission Denied

```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/llms-generator
sudo chown -R www-data:www-data /var/log/llms-generator

# Fix permissions
sudo chmod 755 /opt/llms-generator
sudo chmod 755 /var/log/llms-generator
```

### Service Crashes

```bash
# Check crash logs
sudo journalctl -u llms-api --since "10 minutes ago"

# Increase restart delay
sudo nano /etc/systemd/system/llms-api.service
# Change: RestartSec=30

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart llms-api
```

---

## 🔄 Updates

```bash
# Stop services
sudo systemctl stop llms-api llms-frontend

# Pull latest changes
cd ~/ai-llmstxt-generator/llm_txt_creator
git pull origin main

# Rebuild frontend
npm install
npm run build

# Copy updated files
sudo cp -r backend /opt/llms-generator/
sudo cp -r .next /opt/llms-generator/
sudo cp -r public /opt/llms-generator/

# Update dependencies
cd /opt/llms-generator/backend
sudo pip3 install -r requirements.txt

cd /opt/llms-generator
sudo npm ci --only=production

# Fix permissions
sudo chown -R www-data:www-data /opt/llms-generator

# Start services
sudo systemctl start llms-api llms-frontend
```

---

## 📊 Monitoring

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Automated health check script
cat > /usr/local/bin/llms-health-check.sh << 'EOF'
#!/bin/bash
if ! curl -sf http://localhost:8000/health > /dev/null; then
    echo "Backend down, restarting..."
    systemctl restart llms-api
fi
if ! curl -sf http://localhost:3000 > /dev/null; then
    echo "Frontend down, restarting..."
    systemctl restart llms-frontend
fi
EOF

sudo chmod +x /usr/local/bin/llms-health-check.sh

# Add to cron (every 5 minutes)
echo "*/5 * * * * /usr/local/bin/llms-health-check.sh" | sudo crontab -
```

### Resource Usage

```bash
# Check CPU and memory
systemctl status llms-api llms-frontend

# Detailed resource usage
sudo systemd-cgtop
```

---

## 🎯 Next Steps

- **Automation**: Setup bi-weekly generation with `scripts/setup-cron.sh`
- **Monitoring**: Configure health checks and alerts
- **Backup**: Setup automated backups of generated files
- **Scaling**: Consider load balancing for high traffic

**Need help?** Check the main [README.md](README.md) or open an issue on GitHub.
