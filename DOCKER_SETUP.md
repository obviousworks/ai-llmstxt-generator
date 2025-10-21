# 🐳 Docker Setup Guide

Quick guide to run LLMs.txt Generator with Docker.

## 🚀 Quick Start (3 Steps)

### 1. Clone & Configure

```bash
# Clone repository
git clone https://github.com/obviousworks/ai-llmstxt-generator.git
cd ai-llmstxt-generator/llm_txt_creator

# Create environment file
cp env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

### 2. Build & Run

```bash
# Build and start with Docker Compose
docker-compose up -d

# Or build manually
docker build -t llms-generator .
docker run -d -p 8000:8000 -p 3000:3005 --env-file .env llms-generator
```

### 3. Access Application

- **Frontend**: http://localhost:3005
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

---

## 📊 Docker Commands

### Basic Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Check status
docker-compose ps
```

### Maintenance

```bash
# View backend logs
docker-compose logs -f llms-generator | grep backend

# View frontend logs
docker-compose logs -f llms-generator | grep frontend

# Access container shell
docker-compose exec llms-generator bash

# Rebuild after changes
docker-compose up -d --build
```

---

## 📁 Volume Mounts

The Docker setup creates these directories on your host:

```
./generated/     # Generated llms.txt files
./logs/          # Application logs
./config/        # Configuration files
```

---

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=https://your-domain.com
```

### Port Configuration

Edit `docker-compose.yml` to change ports:

```yaml
ports:
  - "8000:8000"  # Backend: change first number
  - "3000:3005"  # Frontend: change first number
```

---

## 🌐 Production Deployment

### With Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3005;
        proxy_set_header Host $host;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

### With SSL (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

---

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs

# Check if ports are available
sudo lsof -i :8000
sudo lsof -i :3005

# Remove and rebuild
docker-compose down
docker-compose up -d --build
```

### Backend not responding

```bash
# Check backend health
curl http://localhost:8000/health

# View backend logs
docker-compose exec llms-generator cat /app/logs/backend.log
```

### Frontend not loading

```bash
# Check frontend logs
docker-compose exec llms-generator cat /app/logs/frontend.log

# Verify API URL
docker-compose exec llms-generator env | grep NEXT_PUBLIC_API_URL
```

---

## 📈 Performance Tuning

### Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  llms-generator:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Optimize Build

```bash
# Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker-compose build

# Multi-stage build is already optimized in Dockerfile
```

---

## 🔄 Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

---

## ✅ Verification

After starting, verify everything works:

```bash
# 1. Check container is running
docker-compose ps

# 2. Check health
curl http://localhost:8000/health

# 3. Test frontend
curl http://localhost:3005

# 4. Test generation (optional)
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_pages": 5}'
```

---

## 🎯 Next Steps

- Setup automated generation: See `AUTOMATION_SETUP.md`
- Configure Nginx: See `nginx/` directory
- Setup systemd alternative: See `systemd/` directory

**Need help?** Check the main [README.md](README.md) or open an issue on GitHub.
