# Deployment Guide

This document provides step-by-step instructions for deploying the LLMs.txt Generator to production.

## 🚀 Quick Deploy Options

### Option 1: Vercel (Frontend) + Railway (Backend)

This is the recommended approach for fast, reliable deployment.

#### Deploy Backend to Railway

1. **Create Railway Account**
   - Sign up at [railway.app](https://railway.app)
   - Connect your GitHub account

2. **Deploy Backend**
   ```bash
   # Push your code to GitHub first
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```
   
   - In Railway dashboard, click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect Python and deploy

3. **Configure Environment**
   - Railway will automatically install dependencies from `requirements.txt`
   - Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Note your deployed backend URL (e.g., `https://your-app.railway.app`)

#### Deploy Frontend to Vercel

1. **Update API URL**
   ```bash
   # In your project root
   echo "NEXT_PUBLIC_API_URL=https://your-app.railway.app" > .env.local
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Connect your GitHub repo
   - Vercel will auto-deploy
   - Set environment variable `NEXT_PUBLIC_API_URL` in Vercel dashboard

### Option 2: Docker Deployment

#### Build and Run with Docker

1. **Backend Dockerfile**
   ```dockerfile
   # backend/Dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       curl \
       && rm -rf /var/lib/apt/lists/*
   
   # Copy requirements and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application code
   COPY . .
   
   # Expose port
   EXPOSE 8000
   
   # Health check
   HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
       CMD curl -f http://localhost:8000/health || exit 1
   
   # Run the application
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Frontend Dockerfile**
   ```dockerfile
   # Dockerfile
   FROM node:18-alpine AS base
   
   # Install dependencies only when needed
   FROM base AS deps
   RUN apk add --no-cache libc6-compat
   WORKDIR /app
   
   COPY package.json package-lock.json* ./
   RUN npm ci
   
   # Rebuild the source code only when needed
   FROM base AS builder
   WORKDIR /app
   COPY --from=deps /app/node_modules ./node_modules
   COPY . .
   
   RUN npm run build
   
   # Production image, copy all the files and run next
   FROM base AS runner
   WORKDIR /app
   
   ENV NODE_ENV production
   
   RUN addgroup --system --gid 1001 nodejs
   RUN adduser --system --uid 1001 nextjs
   
   COPY --from=builder /app/public ./public
   COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
   COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
   
   USER nextjs
   
   EXPOSE 3000
   
   ENV PORT 3000
   ENV HOSTNAME "0.0.0.0"
   
   CMD ["node", "server.js"]
   ```

3. **Docker Compose**
   ```yaml
   # docker-compose.yml
   version: '3.8'
   
   services:
     backend:
       build: 
         context: ./backend
         dockerfile: Dockerfile
       ports:
         - "8000:8000"
       environment:
         - NODE_ENV=production
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
   
     frontend:
       build: 
         context: .
         dockerfile: Dockerfile
       ports:
         - "3000:3000"
       environment:
         - NEXT_PUBLIC_API_URL=http://backend:8000
       depends_on:
         - backend
   
     # Optional: Nginx reverse proxy
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
       depends_on:
         - frontend
         - backend
   ```

4. **Deploy with Docker**
   ```bash
   # Build and run
   docker-compose up -d
   
   # Check logs
   docker-compose logs -f
   
   # Stop
   docker-compose down
   ```

### Option 3: VPS/Cloud Server

For more control, deploy to a VPS like DigitalOcean, Linode, or AWS EC2.

1. **Server Setup**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install -y python3 python3-pip nodejs npm nginx certbot
   
   # Clone your repository
   git clone <your-repo-url>
   cd llm-txt-generator
   ```

2. **Backend Setup**
   ```bash
   # Set up backend
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Create systemd service
   sudo tee /etc/systemd/system/llms-backend.service > /dev/null <<EOF
   [Unit]
   Description=LLMs.txt Generator Backend
   After=network.target
   
   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/path/to/your/app/backend
   Environment=PATH=/path/to/your/app/backend/venv/bin
   ExecStart=/path/to/your/app/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   EOF
   
   # Start service
   sudo systemctl enable llms-backend
   sudo systemctl start llms-backend
   ```

3. **Frontend Setup**
   ```bash
   # Build frontend
   cd ..
   npm install
   NEXT_PUBLIC_API_URL=http://your-domain:8000 npm run build
   
   # Serve with PM2 (or similar)
   npm install -g pm2
   pm2 start npm --name "llms-frontend" -- start
   pm2 save
   pm2 startup
   ```

4. **Nginx Configuration**
   ```nginx
   # /etc/nginx/sites-available/llms-generator
   server {
       listen 80;
       server_name your-domain.com;
   
       # Frontend
       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_cache_bypass $http_upgrade;
       }
   
       # Backend API
       location /api/ {
           proxy_pass http://localhost:8000/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   ```bash
   # Enable site
   sudo ln -s /etc/nginx/sites-available/llms-generator /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   
   # Optional: SSL with Let's Encrypt
   sudo certbot --nginx -d your-domain.com
   ```

## 🔧 Environment Variables

### Backend
- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## 📊 Monitoring

### Health Checks
- Backend: `GET /health`
- Frontend: Standard Next.js health

### Logs
```bash
# Docker
docker-compose logs -f

# Systemd
sudo journalctl -u llms-backend -f

# PM2
pm2 logs llms-frontend
```

### Performance Monitoring
Consider adding:
- Uptime monitoring (UptimeRobot, Pingdom)
- Error tracking (Sentry)
- Analytics (Google Analytics, Plausible)

## 🔒 Security

### Basic Security Measures
1. **Rate Limiting**: Add rate limiting to prevent abuse
2. **CORS**: Configure CORS properly for production
3. **HTTPS**: Always use HTTPS in production
4. **Input Validation**: Validate all user inputs
5. **Security Headers**: Add security headers via nginx/middleware

### Rate Limiting Example
```python
# Add to main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/generate")
@limiter.limit("5/minute")  # Limit to 5 requests per minute
async def generate_llms_txt(request: Request, data: CrawlRequest):
    # ... existing code
```

## 🚨 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check Python version compatibility
   - Verify all dependencies installed
   - Check port 8000 availability

2. **Frontend can't connect to backend**
   - Verify `NEXT_PUBLIC_API_URL` is correct
   - Check CORS configuration
   - Ensure backend is accessible

3. **Crawling fails**
   - Check target website accessibility
   - Verify network connectivity
   - Check for rate limiting/blocking

4. **Memory issues**
   - Limit concurrent crawls
   - Implement request queuing
   - Add memory monitoring

### Debug Commands
```bash
# Check service status
systemctl status llms-backend

# Check ports
netstat -tlnp | grep :8000

# Check logs
tail -f /var/log/nginx/error.log

# Test API
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_pages": 5}'
```

## 📈 Scaling

For high-traffic deployments:

1. **Load Balancing**: Use multiple backend instances
2. **Queue System**: Add Redis/Celery for background processing
3. **Caching**: Implement Redis caching for results
4. **CDN**: Use CloudFlare or similar for static assets
5. **Database**: Add PostgreSQL for persistent storage

## 🎯 Post-Deployment

1. **Test Everything**: Run full end-to-end tests
2. **Monitor Performance**: Set up monitoring dashboards
3. **Backup Strategy**: Implement regular backups
4. **Update Process**: Plan for updates and maintenance
5. **Documentation**: Keep deployment docs updated

---

🎉 **Congratulations!** Your LLMs.txt Generator is now deployed and ready to help websites create AI-friendly documentation. 