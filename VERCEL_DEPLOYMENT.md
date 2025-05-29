# Deploying to Vercel with Python Functions

This guide shows how to deploy the LLMs.txt Generator using Vercel's serverless functions for the Python backend.

## 🚀 Quick Deploy

### 1. Prepare Your Repository

Make sure your project structure looks like this:
```
llm-txt-generator/
├── api/                    # Vercel functions
│   ├── generate.py        # Main generation endpoint
│   └── health.py          # Health check endpoint
├── src/                   # Next.js frontend
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel configuration
└── package.json          # Node.js dependencies
```

### 2. Deploy to Vercel

#### Option A: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

#### Option B: Deploy via GitHub Integration

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Vercel function support"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Connect your GitHub repository
   - Vercel will automatically detect and deploy

### 3. Configure Environment Variables

In your Vercel dashboard:

1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add the following:

```
NEXT_PUBLIC_API_URL = https://your-app.vercel.app
```

Or if you want to use the same domain for both frontend and API (recommended):
```
NEXT_PUBLIC_API_URL = 
```
(Leave empty to use relative URLs)

## 📁 File Structure Explanation

### `api/generate.py`
This is the main serverless function that handles website crawling and llms.txt generation. It:
- Uses the `BaseHTTPRequestHandler` class (required for Vercel Python functions)
- Handles CORS headers for cross-origin requests
- Implements the same crawling logic as the original FastAPI backend
- Returns JSON responses compatible with the frontend

### `api/health.py`
A simple health check endpoint that returns the API status.

### `requirements.txt`
Contains only the essential Python dependencies:
- `beautifulsoup4` - HTML parsing
- `aiohttp` - Async HTTP requests

### `vercel.json`
Configuration file that tells Vercel:
- Which files are Python functions
- How to route requests to the functions
- Runtime configuration (Python 3.9)

## 🔧 Configuration Details

### Vercel Function Limitations

Vercel functions have some limitations to be aware of:

1. **Execution Time**: 10 seconds for Hobby plan, 60 seconds for Pro
2. **Memory**: 1024MB max
3. **Payload Size**: 4.5MB request/response limit
4. **Cold Starts**: Functions may have cold start delays

### Optimizations for Vercel

The Vercel function implementation includes several optimizations:

1. **Reduced Dependencies**: Only essential packages are included
2. **Timeout Handling**: Shorter timeouts to prevent function timeouts
3. **Error Handling**: Proper error responses for debugging
4. **CORS Support**: Built-in CORS headers for frontend compatibility

## 🚀 Testing Your Deployment

### 1. Test the Health Endpoint
```bash
curl https://your-app.vercel.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "LLMs.txt Generator API is running",
  "version": "1.0.0"
}
```

### 2. Test the Generation Endpoint
```bash
curl -X POST "https://your-app.vercel.app/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://fastapi.tiangolo.com",
    "max_pages": 10,
    "depth_limit": 2
  }'
```

### 3. Test the Frontend
Visit `https://your-app.vercel.app` and try generating an llms.txt file.

## 🔄 Updating Your Deployment

### For Code Changes
```bash
# Make your changes, then:
git add .
git commit -m "Update functionality"
git push origin main

# Vercel will automatically redeploy
```

### For Environment Variables
1. Go to Vercel dashboard
2. Project Settings → Environment Variables
3. Update variables
4. Redeploy if needed

## 🐛 Troubleshooting

### Common Issues

1. **Function Timeout**
   - Reduce `max_pages` in requests
   - Check target website response times
   - Consider implementing pagination

2. **Import Errors**
   - Verify all dependencies are in `requirements.txt`
   - Check Python version compatibility

3. **CORS Issues**
   - Verify CORS headers in function responses
   - Check `NEXT_PUBLIC_API_URL` configuration

4. **Cold Start Delays**
   - First request may be slow (normal for serverless)
   - Consider implementing a warming strategy

### Debug Commands

```bash
# Check Vercel logs
vercel logs

# Test locally with Vercel CLI
vercel dev

# Check function status
curl https://your-app.vercel.app/api/health
```

## 📊 Monitoring

### Vercel Analytics
- Enable Vercel Analytics in your dashboard
- Monitor function execution times
- Track error rates

### Custom Monitoring
Add logging to your functions:

```python
import logging
logging.basicConfig(level=logging.INFO)

# In your function:
logging.info(f"Processing request for URL: {url}")
```

## 🔒 Security Considerations

### Rate Limiting
Consider implementing rate limiting to prevent abuse:

```python
# Simple rate limiting example
import time
from collections import defaultdict

request_counts = defaultdict(list)

def is_rate_limited(ip_address, max_requests=5, window_minutes=1):
    now = time.time()
    window_start = now - (window_minutes * 60)
    
    # Clean old requests
    request_counts[ip_address] = [
        req_time for req_time in request_counts[ip_address] 
        if req_time > window_start
    ]
    
    # Check if over limit
    if len(request_counts[ip_address]) >= max_requests:
        return True
    
    # Add current request
    request_counts[ip_address].append(now)
    return False
```

### Input Validation
The functions include basic input validation, but consider adding:
- URL whitelist/blacklist
- Content-type validation
- Request size limits

## 💰 Cost Considerations

### Vercel Pricing
- **Hobby Plan**: 100GB-hours of function execution per month (free)
- **Pro Plan**: 1000GB-hours included, then $0.18 per additional GB-hour

### Optimization Tips
1. **Reduce Function Execution Time**: Limit crawling scope
2. **Implement Caching**: Cache results for popular sites
3. **Use Edge Functions**: For simple operations when possible

## 🎯 Next Steps

After successful deployment:

1. **Custom Domain**: Add your custom domain in Vercel settings
2. **SSL Certificate**: Automatically provided by Vercel
3. **Analytics**: Enable Vercel Analytics for insights
4. **Monitoring**: Set up uptime monitoring
5. **Caching**: Implement Redis caching for better performance

## 📚 Additional Resources

- [Vercel Functions Documentation](https://vercel.com/docs/functions)
- [Python on Vercel](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Vercel CLI Reference](https://vercel.com/docs/cli)

---

🎉 **Congratulations!** Your LLMs.txt Generator is now running on Vercel with serverless Python functions! 