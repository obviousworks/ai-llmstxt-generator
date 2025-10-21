# 🔄 Refactoring Plan: Self-Hosted Open Source Deployment

**Branch**: `feature/self-hosted-deployment`  
**Goal**: Remove Vercel dependencies, enable self-hosted deployment with automated bi-weekly generation  
**Status**: 🚧 In Progress

---

## 🎯 **Project Goals**

### ✅ **What We Want:**
1. **Open Source** - Keep the project freely available
2. **Self-Hosted** - Anyone can run on their own server or locally
3. **Automated** - Bi-weekly generation (every 2 weeks) with cron jobs
4. **Vercel-Free** - No cloud platform dependencies
5. **Easy Setup** - Docker, Systemd, or manual installation options

### ❌ **What We Remove:**
- All Vercel-specific code and configuration
- Cloud platform dependencies
- Vercel URLs and references

---

## 📋 **Implementation Phases**

### **Phase 1: Cleanup - Remove Vercel** ✂️

**Status**: 🔴 Not Started

#### Files to Delete:
- [ ] `vercel.json` - Vercel deployment configuration
- [ ] `deploy-vercel.sh` - Vercel deployment script
- [ ] `api/` directory - Vercel serverless functions (if exists)

#### Files to Modify:
- [ ] `README.md` - Remove all Vercel references and sections
- [ ] `app/layout.tsx` - Change `metadataBase` URL from vercel.app
- [ ] `app/llms.txt` - Remove vercel.app URLs
- [ ] `app/llms-full.txt` - Remove vercel.app URLs
- [ ] Search entire codebase for "vercel" references

#### Verification:
```bash
# Search for remaining Vercel references
grep -r "vercel" . --exclude-dir=node_modules --exclude-dir=.git
```

---

### **Phase 2: Docker Setup** 🐳

**Status**: 🔴 Not Started

#### Files to Create:

**`docker-compose.yml`**
```yaml
version: '3.8'
services:
  llms-generator:
    build: .
    ports:
      - "8000:8000"  # Backend API
      - "3000:3000"  # Frontend
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./generated:/app/generated
      - ./logs:/app/logs
    restart: unless-stopped
```

**`Dockerfile`**
```dockerfile
# Multi-stage build for production
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ ./backend/

# Copy built frontend
COPY --from=frontend-builder /app/.next ./frontend/.next
COPY --from=frontend-builder /app/public ./frontend/public
COPY --from=frontend-builder /app/package*.json ./frontend/

# Create directories
RUN mkdir -p /app/generated /app/logs

# Expose ports
EXPOSE 8000 3000

# Start script
COPY docker-start.sh .
RUN chmod +x docker-start.sh
CMD ["./docker-start.sh"]
```

**`docker-start.sh`**
```bash
#!/bin/bash
set -e

echo "Starting LLMs.txt Generator..."

# Start backend
cd /app/backend
python3 run_dev.py &
BACKEND_PID=$!

# Start frontend
cd /app/frontend
npm start &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
```

**`.dockerignore`**
```
node_modules
.next
.git
.env
*.log
__pycache__
*.pyc
.vercel
```

#### Testing Checklist:
- [ ] `docker-compose build` succeeds
- [ ] `docker-compose up` starts both services
- [ ] Backend accessible at http://localhost:8000
- [ ] Frontend accessible at http://localhost:3005
- [ ] Generation works end-to-end

---

### **Phase 3: Systemd Services** ⚙️

**Status**: 🔴 Not Started

#### Directory Structure:
```
systemd/
├── llms-api.service
├── llms-frontend.service
└── install.sh
```

**`systemd/llms-api.service`**
```ini
[Unit]
Description=LLMs.txt Generator API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/llms-generator/backend
Environment=OPENAI_API_KEY=your-key-here
ExecStart=/usr/bin/python3 run_dev.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**`systemd/llms-frontend.service`**
```ini
[Unit]
Description=LLMs.txt Generator Frontend
After=network.target llms-api.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/llms-generator
Environment=NEXT_PUBLIC_API_URL=http://localhost:8000
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**`systemd/install.sh`**
```bash
#!/bin/bash
set -e

echo "Installing LLMs.txt Generator systemd services..."

# Copy service files
sudo cp llms-api.service /etc/systemd/system/
sudo cp llms-frontend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable llms-api llms-frontend

# Start services
sudo systemctl start llms-api llms-frontend

echo "✅ Services installed and started!"
echo "Check status with: sudo systemctl status llms-api llms-frontend"
```

---

### **Phase 4: Automation Scripts** ⏰

**Status**: 🔴 Not Started

#### Directory Structure:
```
scripts/
├── generate-llms.sh       # Main generation script
├── deploy-llms.sh         # Deployment script
├── setup-cron.sh          # Cron installation
└── health-check.sh        # Health monitoring
```

**`scripts/generate-llms.sh`**
```bash
#!/bin/bash
# Generates llms.txt files for configured websites
# Usage: ./generate-llms.sh

set -e

# Load configuration
source "$(dirname "$0")/../config/websites.conf"

API_URL="${API_URL:-http://localhost:8000}"
OUTPUT_DIR="${OUTPUT_DIR:-/var/www/generated-llms}"
LOG_FILE="${LOG_FILE:-/var/log/llms-generator.log}"

mkdir -p "$OUTPUT_DIR"

echo "$(date): Starting bi-weekly llms.txt generation" | tee -a "$LOG_FILE"

for website in "${WEBSITES[@]}"; do
    echo "$(date): Processing $website" | tee -a "$LOG_FILE"
    
    domain=$(echo "$website" | sed 's|https\?://||' | sed 's|/.*||')
    
    # Generate llms.txt
    response=$(curl -X POST "$API_URL/generate" \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"$website\", \"max_pages\": 20}" \
        --silent --show-error)
    
    # Extract and save files
    echo "$response" | python3 -c "
import json, sys
data = json.load(sys.stdin)
with open('$OUTPUT_DIR/${domain}_llms.txt', 'w') as f:
    f.write(data['llms_txt'])
with open('$OUTPUT_DIR/${domain}_llms-full.txt', 'w') as f:
    f.write(data['llms_full_txt'])
print('✅ Generated files for $domain')
    " | tee -a "$LOG_FILE"
    
    sleep 5  # Rate limiting
done

echo "$(date): Generation completed" | tee -a "$LOG_FILE"
```

**`scripts/deploy-llms.sh`**
```bash
#!/bin/bash
# Deploys generated llms.txt files to target websites
# Usage: ./deploy-llms.sh

set -e

source "$(dirname "$0")/../config/websites.conf"

OUTPUT_DIR="${OUTPUT_DIR:-/var/www/generated-llms}"
LOG_FILE="${LOG_FILE:-/var/log/llms-deployment.log}"

echo "$(date): Starting deployment" | tee -a "$LOG_FILE"

for domain in "${!DEPLOY_TARGETS[@]}"; do
    source_llms="$OUTPUT_DIR/${domain}_llms.txt"
    source_full="$OUTPUT_DIR/${domain}_llms-full.txt"
    target="${DEPLOY_TARGETS[$domain]}"
    
    if [ ! -f "$source_llms" ]; then
        echo "$(date): ⚠️  No files found for $domain" | tee -a "$LOG_FILE"
        continue
    fi
    
    if [[ "$target" == *"@"* ]]; then
        # Remote deployment via SCP
        scp "$source_llms" "$target/llms.txt"
        scp "$source_full" "$target/llms-full.txt"
        echo "$(date): ✅ Deployed $domain remotely" | tee -a "$LOG_FILE"
    else
        # Local deployment
        cp "$source_llms" "$target/llms.txt"
        cp "$source_full" "$target/llms-full.txt"
        echo "$(date): ✅ Deployed $domain locally" | tee -a "$LOG_FILE"
    fi
done

echo "$(date): Deployment completed" | tee -a "$LOG_FILE"
```

**`scripts/setup-cron.sh`**
```bash
#!/bin/bash
# Sets up cron jobs for automated generation
# Usage: sudo ./setup-cron.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CRON_SCHEDULE="${CRON_SCHEDULE:-0 2 */14 * *}"  # Every 2 weeks at 2 AM

echo "Setting up cron jobs for LLMs.txt Generator..."

# Create cron job
(crontab -l 2>/dev/null || true; echo "$CRON_SCHEDULE $SCRIPT_DIR/generate-llms.sh && $SCRIPT_DIR/deploy-llms.sh") | crontab -

echo "✅ Cron job installed!"
echo "Schedule: $CRON_SCHEDULE (every 2 weeks)"
echo "View with: crontab -l"
```

**`scripts/health-check.sh`**
```bash
#!/bin/bash
# Health check and auto-restart
# Usage: ./health-check.sh

API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3005}"

# Check API
if ! curl -sf "$API_URL/health" > /dev/null; then
    echo "$(date): ⚠️  API down, restarting..."
    sudo systemctl restart llms-api
fi

# Check Frontend
if ! curl -sf "$FRONTEND_URL" > /dev/null; then
    echo "$(date): ⚠️  Frontend down, restarting..."
    sudo systemctl restart llms-frontend
fi
```

#### Configuration File:

**`config/websites.conf`**
```bash
#!/bin/bash
# Configuration for automated llms.txt generation

# API Configuration
API_URL="http://localhost:8000"
OUTPUT_DIR="/var/www/generated-llms"
LOG_FILE="/var/log/llms-generator.log"

# Websites to generate llms.txt for
WEBSITES=(
    "https://obviousworks.ch"
    "https://your-website.com"
    "https://another-site.com"
)

# Deployment targets (domain => path)
declare -A DEPLOY_TARGETS=(
    ["obviousworks.ch"]="/var/www/obviousworks/public"
    ["your-website.com"]="/var/www/your-site/public"
    ["another-site.com"]="user@server:/var/www/html"
)

# Cron schedule (default: every 2 weeks)
CRON_SCHEDULE="0 2 */14 * *"
```

---

### **Phase 5: Nginx Configuration** 🌐

**Status**: 🔴 Not Started

**`nginx/llms-generator.conf`**
```nginx
# LLMs.txt Generator - Nginx Configuration

upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3005;
}

server {
    listen 80;
    server_name llms-generator.your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name llms-generator.your-domain.com;
    
    # SSL Configuration (use certbot for Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for long-running generations
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
```

**`nginx/install.sh`**
```bash
#!/bin/bash
# Install Nginx configuration

set -e

echo "Installing Nginx configuration..."

sudo cp llms-generator.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/llms-generator.conf /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

echo "✅ Nginx configuration installed!"
```

---

### **Phase 6: README Rewrite** 📚

**Status**: 🔴 Not Started

#### New README Structure:

```markdown
# 🚀 LLMs.txt Generator - Self-Hosted & Open Source

> Open source tool for automated llms.txt generation with bi-weekly updates

## 🎯 Quick Start (3 Options)

### Option 1: Docker (Recommended)
### Option 2: Systemd Services  
### Option 3: Local Development

## 📦 Installation

### Prerequisites
### Docker Setup
### Manual Setup

## ⏰ Automated Bi-Weekly Generation

### Quick Setup
### Configuration
### Custom Schedules

## 🔧 Configuration

### Environment Variables
### Website Configuration
### Deployment Targets

## 🌐 Public Access

### Nginx Setup
### SSL/HTTPS
### Domain Configuration

## 📊 Monitoring & Maintenance

### Logs
### Health Checks
### Troubleshooting

## 🏢 About ObviousWorks

[Keep existing content]
```

#### Sections to Remove:
- ❌ All Vercel deployment sections
- ❌ Vercel cron job explanations
- ❌ Vercel-specific troubleshooting
- ❌ Vercel CLI commands

#### Sections to Add:
- ✅ Docker deployment guide
- ✅ Systemd services setup
- ✅ Linux cron job setup
- ✅ Nginx configuration
- ✅ Multi-domain automation
- ✅ Self-hosted deployment strategies

---

## 📊 **Progress Tracking**

### Completed: ✅
- [x] Create feature branch
- [x] Create refactoring plan

### In Progress: 🟡
- [ ] Phase 1: Cleanup
- [ ] Phase 2: Docker Setup
- [ ] Phase 3: Systemd Services
- [ ] Phase 4: Automation Scripts
- [ ] Phase 5: Nginx Configuration
- [ ] Phase 6: README Rewrite

### Testing: 🧪
- [ ] Docker deployment test
- [ ] Systemd deployment test
- [ ] Cron job test
- [ ] Multi-domain test
- [ ] End-to-end test

---

## 🎯 **Success Criteria**

### ✅ **Must Have:**
1. Complete Vercel removal
2. Working Docker setup
3. Working Systemd setup
4. Automated bi-weekly generation scripts
5. Comprehensive README
6. All tests passing

### 🎁 **Nice to Have:**
- Nginx configuration examples
- Health monitoring scripts
- Multiple deployment examples
- Video tutorial

---

## 📝 **Notes**

- Keep all changes in `feature/self-hosted-deployment` branch
- Test each phase before moving to next
- Update this plan as we progress
- Commit frequently with clear messages

---

**Last Updated**: October 15, 2025  
**Branch**: `feature/self-hosted-deployment`  
**Status**: 🚧 Phase 1 Ready to Start
