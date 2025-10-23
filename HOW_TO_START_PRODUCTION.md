# Production Deployment Guide

This guide explains how to deploy and run the LLMs.txt Generator in **production mode** on a server.

## Prerequisites

- Node.js 18+ installed
- Python 3.8+ installed
- Nginx configured as reverse proxy
- Server with ports 5001 (Frontend) and 8000 (Backend) available

## Initial Setup (One-time)

### 1. Clone Repository

```bash
cd /opt
git clone <repository-url> ai-llmstxt-generator
cd ai-llmstxt-generator
```

### 2. Install Dependencies

**Frontend:**
```bash
npm install
```

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
```

### 3. Configure Environment

Create `.env` file in project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Build Frontend

```bash
npm run build
```

This creates an optimized production build in `.next/` directory.

## Starting Production Servers

### Option 1: Manual Start

**Start Backend:**
```bash
cd /opt/ai-llmstxt-generator/backend
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
cd ..
```

**Start Frontend:**
```bash
cd /opt/ai-llmstxt-generator
NODE_ENV=production npm run start -- --port 5001 &
```

### Option 2: Using Production Script

Use the provided `start-production.sh` script:

```bash
/opt/ai-llmstxt-generator/start-production.sh
```

## Stopping Servers

```bash
# Stop Next.js
pkill -f "next"

# Stop Backend
pkill -f "uvicorn"
```

## Updating Application

When you make changes and want to deploy:

```bash
cd /opt/ai-llmstxt-generator

# 1. Pull latest changes
git pull origin feature/self-hosted-deployment

# 2. Stop running servers
pkill -9 -f "next"
pkill -9 -f "uvicorn"

# 3. Rebuild frontend (if code changed)
rm -rf .next
npm run build

# 4. Restart servers
/opt/ai-llmstxt-generator/start-production.sh
```

## Nginx Configuration

The app runs behind Nginx reverse proxy at `/llm-text-generator`.

**Required Nginx config** (`/etc/nginx/sites-available/www.obviousworks.ch`):

```nginx
### llm-text-generator START
# API-Location (highest priority)
location ^~ /llm-text-generator/api/ {
  proxy_pass http://localhost:8000/;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_buffering off;
}

# Next.js Location (^~ overrides WordPress try_files!)
location ^~ /llm-text-generator {
  proxy_pass http://localhost:5001/llm-text-generator;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_buffering off;
}
### llm-text-generator END
```

**Important:** Place this config **AFTER** `include /etc/nginx/wordpress.conf;` and use `^~` to override WordPress routing!

After config changes:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Verification

### Check if servers are running:
```bash
ps aux | grep -E "(next|uvicorn)"
```

### Test Frontend (local):
```bash
curl -I http://localhost:5001/llm-text-generator
# Should return: HTTP/1.1 200 OK
```

### Test Backend (local):
```bash
curl -I http://localhost:8000/docs
# Should return: HTTP/1.1 200 OK
```

### Test via Nginx (external):
```bash
curl -I https://www.obviousworks.ch/llm-text-generator
# Should return: HTTP/2 200
```

### Test API via Nginx:
```bash
curl -X POST https://www.obviousworks.ch/llm-text-generator/api/generate \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","max_pages":5}'
```

## Troubleshooting

### Assets not loading (404 errors)

**Symptom:** CSS, JS files return 404
**Cause:** Running in dev mode instead of production
**Solution:** 
```bash
pkill -f "next"
NODE_ENV=production npm run start -- --port 5001 &
```

### API returns 502 Bad Gateway

**Symptom:** API requests fail with 502
**Cause:** Backend not running
**Solution:**
```bash
cd /opt/ai-llmstxt-generator/backend
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
```

### WordPress interfering with routes

**Symptom:** Nginx error log shows: `open() "/var/www/vhosts/obviousworks/llm-text-generator/..."`
**Cause:** WordPress `try_files` matching before Next.js location
**Solution:** Ensure `^~` is used in location directive and config is placed AFTER wordpress.conf

### Redirect loop

**Symptom:** Browser shows ERR_TOO_MANY_REDIRECTS
**Cause:** Incorrect trailing slash configuration
**Solution:** Use config exactly as shown above (no trailing slash in location, basePath in proxy_pass)

## Important Notes

- ✅ **Always use production build** (`npm run build` + `npm run start`)
- ❌ **Never use dev mode** (`npm run dev`) in production
- ✅ **basePath is required** in `next.config.ts` for subpath deployment
- ✅ **Use `^~` in Nginx** to override WordPress routing
- ✅ **Place config AFTER wordpress.conf** in main nginx config

## Monitoring

### Check logs:

**Frontend logs:**
```bash
# If running in foreground, check terminal output
# For background process, redirect to log file:
NODE_ENV=production npm run start -- --port 5001 > /var/log/llm-txt-frontend.log 2>&1 &
```

**Backend logs:**
```bash
# Check uvicorn output
tail -f /var/log/llm-txt-backend.log
```

**Nginx logs:**
```bash
sudo tail -f /var/log/nginx/obviousworks.ch/access.log
sudo tail -f /var/log/nginx/obviousworks.ch/error.log
```

## Production Checklist

Before going live:

- [ ] Environment variables set (`.env` with `OPENAI_API_KEY`)
- [ ] Frontend built (`npm run build` completed)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5001 (production mode)
- [ ] Nginx config updated and reloaded
- [ ] All tests passing (curl commands above)
- [ ] No 404 errors in browser console
- [ ] API requests working (test generate endpoint)

## Support

For issues, check:
1. Nginx error logs
2. Process status (`ps aux | grep -E "(next|uvicorn)"`)
3. Port availability (`netstat -tulpn | grep -E "(5001|8000)"`)
4. This guide's troubleshooting section
