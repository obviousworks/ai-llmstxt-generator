# 🚀 Vercel Deployment Guide

Complete guide for deploying the LLMs.txt Generator to Vercel with serverless Python functions.

## 🎯 Quick Deploy

**Use the automated deployment script:**
```bash
./deploy-vercel.sh
```

This script handles everything automatically:
- ✅ Validates all required files
- ✅ Builds the Next.js application  
- ✅ Deploys to Vercel with Python functions
- ✅ Provides testing instructions

## 📋 Prerequisites

1. **Vercel CLI installed**
   ```bash
   npm install -g vercel
   ```

2. **Vercel account** - Sign up at [vercel.com](https://vercel.com)

3. **Login to Vercel**
   ```bash
   vercel login
   ```

## 🛠 Manual Deployment

If you prefer manual deployment:

### 1. Prepare the Project
```bash
# Build the frontend
npm run build

# Verify required files exist
ls api/generate.py api/health.py requirements.txt vercel.json
```

### 2. Deploy to Vercel
```bash
# Deploy to production
vercel --prod
```

### 3. Test the Deployment
```bash
# Test health endpoint
curl https://your-app.vercel.app/api/health

# Test generation (replace with your URL)
curl -X POST https://your-app.vercel.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_pages": 5}'
```

## 📁 Required Files

The deployment requires these files:

```
llm-txt-generator/
├── api/
│   ├── generate.py       # Main crawling function
│   └── health.py         # Health check function
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
├── src/app/page.tsx     # Frontend application
└── package.json         # Node.js dependencies
```

## ⚙️ Configuration

### vercel.json
```json
{
  "routes": [
    {
      "src": "/api/generate",
      "dest": "/api/generate.py"
    },
    {
      "src": "/api/health", 
      "dest": "/api/health.py"
    }
  ]
}
```

### requirements.txt
```
beautifulsoup4==4.13.4
aiohttp==3.12.2
```

## 🔧 Environment Variables

**No environment variables required!** 

The frontend automatically detects the deployment environment:
- **Local**: Uses `http://localhost:8000` 
- **Production**: Uses relative paths to Vercel functions

## ⚡ Performance & Limits

### Vercel Function Limits
- **Execution Time**: 10s (Hobby) / 60s (Pro)
- **Memory**: 1024MB maximum
- **Payload**: 4.5MB request/response limit
- **Cold Start**: ~1-3 seconds for Python functions

### Optimization Tips
- Use `max_pages: 20` or less for faster processing
- Consider `depth_limit: 3` to control scope
- Large sites may need Pro plan for longer execution time

## 🐛 Troubleshooting

### Common Issues

**1. Function Timeout**
```
Error: Function execution timed out
```
- Reduce `max_pages` parameter
- Upgrade to Vercel Pro for 60s limit

**2. Memory Limit**
```
Error: Function exceeded memory limit
```
- Reduce crawl scope with `depth_limit`
- Use smaller `max_pages` values

**3. Cold Start Delays**
```
First request takes 3+ seconds
```
- This is normal for serverless functions
- Subsequent requests will be faster

**4. Import Errors**
```
ModuleNotFoundError: No module named 'aiohttp'
```
- Verify `requirements.txt` is in project root
- Check dependencies are correctly specified

### Debug Steps

1. **Check function logs**
   ```bash
   vercel logs your-deployment-url
   ```

2. **Test locally first**
   ```bash
   ./start.sh
   curl http://localhost:3000
   ```

3. **Verify build**
   ```bash
   npm run build
   ```

## 🔄 Updates & Redeployment

To update your deployment:

```bash
# Make your changes
git add .
git commit -m "Update feature"

# Redeploy
./deploy-vercel.sh
```

Or manually:
```bash
vercel --prod
```

## 📊 Monitoring

### Check Deployment Status
- Visit [Vercel Dashboard](https://vercel.com/dashboard)
- Monitor function execution times
- Review error logs and analytics

### Performance Monitoring
```bash
# Test response times
time curl https://your-app.vercel.app/api/health

# Monitor function execution
vercel logs --follow
```

## 🎉 Success!

After successful deployment:

1. ✅ Frontend available at: `https://your-app.vercel.app`
2. ✅ API health check: `https://your-app.vercel.app/api/health`
3. ✅ Generation endpoint: `https://your-app.vercel.app/api/generate`

Your LLMs.txt Generator is now live and ready to use! 🚀

---

**Need help?** Check the [main README](README.md) or create an issue. 