# 🤖 LLMs.txt Generator with Automated Monitoring

An intelligent web application that generates `llms.txt` files for websites and automatically monitors them for changes. This tool follows the [llms.txt specification](https://llmstxt.org/) to create AI-friendly documentation files that help Large Language Models better understand website content.

## 🆕 Improved Documentation Structure

This README has been restructured for better user experience:
- **📋 Grouped sections**: Related topics are now organized together
- **🎬 Quick Demo**: Try it in 30 seconds with visual examples
- **🚀 Progressive flow**: Getting Started → Architecture → Advanced Topics
- **🔧 Consolidated config**: All settings in one comprehensive section
- **📚 Better navigation**: Grouped table of contents for easier browsing

## 📋 Table of Contents

### 🚀 Getting Started
- [✨ Features](#-features)
- [🎬 Quick Demo](#-quick-demo)
- [🛠 Technology Stack](#-technology-stack)
- [📦 Installation & Setup](#-installation--setup)
- [🎯 Usage](#-usage)

### 🏗️ Architecture & Setup  
- [📁 Project Structure](#-project-structure)
- [🔧 Configuration](#-configuration)
- [🚢 Deployment](#-deployment)
- [⏰ Automated Monitoring Setup](#-automated-monitoring-setup)

### 📚 Advanced Topics
- [📊 Understanding Change Detection](#-understanding-change-detection)
- [⚡ Performance & Scaling](#-performance--scaling)
- [🧪 Testing](#-testing)
- [🐛 Troubleshooting](#-troubleshooting)

### 🤝 Community
- [🚀 Future Enhancements](#-future-enhancements)
- [🤝 Contributing](#-contributing)
- [📋 Quick Reference](#-quick-reference)

## ✨ Features

### Core Generation
- **Intelligent Website Crawling**: Automatically discovers and analyzes website pages
- **AI-Enhanced Content**: Uses OpenAI to improve descriptions and organization
- **Smart Categorization**: Dynamic section organization based on content themes
- **Dual File Generation**: Creates both `llms.txt` (curated) and `llms-full.txt` (comprehensive)
- **Existing File Detection**: Automatically uses existing llms.txt files when found

### Automated Monitoring (NEW!)
- **🔄 Smart Change Detection**: Monitors website structure changes automatically
- **📅 Flexible Scheduling**: From hourly to weekly check intervals
- **🎯 Intelligent Updates**: Only regenerates when significant changes detected
- **📊 Change Analytics**: Detailed reports on what changed and why
- **🤖 Auto-scaling AI**: Processing scales with website size

### Modern Interface
- **Beautiful UI**: Responsive design built with Next.js and Tailwind CSS
- **Real-time Progress**: Live feedback during crawling and generation
- **Monitoring Dashboard**: Comprehensive interface for managing automated updates
- **Instant Downloads**: Direct download of generated files

## 🎬 Quick Demo

### Try It in 30 Seconds
```bash
# Clone and start (automated setup)
git clone <your-repo-url> && cd llm_txt_creator
./start.sh

# Open browser to http://localhost:3000
# Enter a website URL (e.g., https://docs.anthropic.com)
# Click "Generate llms.txt" and watch the magic! ✨
```

### What You'll See
1. **Real-time crawling**: Pages discovered and analyzed live
2. **AI enhancement**: Content improved and categorized automatically  
3. **Dual outputs**: Both curated and comprehensive versions
4. **Monitoring setup**: Add sites for automatic updates

### Example Output
```
# Anthropic Documentation
> AI safety company building reliable, interpretable, and steerable AI systems

## Getting Started
- Quickstart Guide - Essential setup and first API calls
- Authentication - API key setup and security best practices

## API Reference  
- Messages API - Core conversational AI interface
- Streaming - Real-time response handling
...
```

## 🛠 Technology Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Modern styling
- **Lucide React** - Beautiful icons

### Backend
- **Vercel Functions** - Serverless Python functions for production
- **FastAPI** - Local development server with hot reload
- **OpenAI GPT-4** - AI-enhanced content processing
- **aiohttp** - Async HTTP client for web crawling
- **BeautifulSoup4** - HTML parsing and content extraction

### Automation
- **Vercel Cron Jobs** - Automatic scheduling every 6 hours
- **Change Detection** - Structure fingerprinting and diff analysis
- **Smart Thresholds** - Updates only for significant changes (5%+)

## 📁 Project Structure

```
llm_txt_creator/                   # Root project directory
├── app/                           # 🎨 FRONTEND (Next.js)
│   ├── page.tsx                  # Main generator interface
│   ├── monitor/                  # Monitoring dashboard
│   │   └── page.tsx             # /monitor route
│   ├── layout.tsx               # App-wide layout
│   └── globals.css              # Global styles
├── api/                           # ☁️ PRODUCTION API (Vercel Functions)
│   ├── generate.py              # Main generation endpoint
│   ├── scheduler.py             # Monitoring management
│   ├── cron.py                  # Automated scheduling
│   └── health.py                # Health checks
├── backend/                       # 🔧 DEVELOPMENT API (FastAPI)
│   ├── main.py                  # Main API (equivalent to api/generate.py)
│   ├── scheduler.py             # Scheduler service (equivalent to api/scheduler.py)
│   └── run_dev.py               # Development server runner
├── vercel.json                   # Deployment config with cron jobs
├── package.json                 # Frontend dependencies
└── requirements.txt             # Python dependencies
```

### How The Two APIs Work Together

**Development Mode (Local):**
```
Frontend (localhost:3000) 
    ↓
Backend FastAPI (localhost:8000) - Main API
    ↓
Backend FastAPI (localhost:8001) - Scheduler API
```

**Production Mode (Vercel):**
```
Frontend (yourapp.vercel.app)
    ↓
Vercel Functions (/api/generate, /api/scheduler, /api/cron)
    ↓
Automatic Cron Jobs (every 6 hours)
```

## 📦 Installation & Setup

### Prerequisites
- **Node.js 18+** (for frontend)
- **Python 3.9+** (for local backend development)
- **OpenAI API Key** (for AI enhancement)
- **Vercel CLI** (for deployment)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd llm_txt_creator
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env_example .env
   ```
   
   Edit `.env` with your OpenAI API key:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Start development servers**
   
   **Option A: Use the automated start script (Recommended)**
   ```bash
   ./start.sh
   ```
   
   This script automatically:
   - Creates Python virtual environment if needed
   - Installs all backend dependencies
   - Starts both FastAPI servers (ports 8000 & 8001)
   - Starts Next.js development server (port 3000)
   - Provides clear status messages and error handling
   
   **Option B: Use the convenience script**
   ```bash
   cd backend
   python run_dev.py
   ```
   
   **Option C: Manual startup**
   ```bash
   # Terminal 1 - Main API
   cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   
   # Terminal 2 - Scheduler Service  
   cd backend && python -m uvicorn scheduler:scheduler_app --host 0.0.0.0 --port 8001 --reload
   
   # Terminal 3 - Frontend
   npm run dev
   ```

5. **Open your browser**
   - **Main App**: http://localhost:3000
   - **Monitor Dashboard**: http://localhost:3000/monitor
   - **API Docs**: http://localhost:8000/docs
   - **Scheduler Docs**: http://localhost:8001/docs

## 🎯 Usage

### Basic Generation

1. **Enter Website URL**: Input the URL you want to analyze
2. **Configure Settings**: Choose maximum pages to crawl (10-100)
3. **Generate Files**: Click "Generate llms.txt" and wait for processing
4. **Download Results**: Download both `llms.txt` and `llms-full.txt` files
5. **Review Analysis**: View the pages analyzed and their importance scores

### 🔄 Automated Monitoring (NEW!)

#### Adding Sites to Monitoring

1. Navigate to `/monitor` page
2. Enter website URL (e.g., `https://docs.anthropic.com`)
3. Choose check interval (recommended: 24 hours)
4. Select max pages to crawl (recommended: 20 pages)
5. Click "Add to Monitoring"

#### How Monitoring Works

**Change Detection:**
- Creates "fingerprints" of website structure (URLs, titles, sections)
- Detects new pages, removed pages, and modified content
- Calculates change severity: Major (50%+), Moderate (20%+), Minor (5%+)

**Smart Updates:**
- Only regenerates llms.txt when changes are significant (5%+ threshold)
- AI processing scales with site size to prevent timeouts
- Detailed change reports show exactly what changed

**Automatic Scheduling:**
- **Production**: Cron jobs run every 6 hours automatically
- **Configurable**: Set custom intervals from hourly to weekly
- **Manual Override**: Force immediate checks anytime

### API Usage

#### Local Development API

```bash
# Generate llms.txt
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.anthropic.com",
    "max_pages": 20,
    "depth_limit": 3
  }'

# Add site to monitoring
curl -X POST "http://localhost:8001/scheduler" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add_site",
    "url": "https://docs.anthropic.com",
    "max_pages": 20,
    "check_interval": 86400
  }'

# Check for updates
curl -X POST "http://localhost:8001/scheduler" \
  -H "Content-Type: application/json" \
  -d '{"action": "check_updates"}'
```

#### Production API (Vercel)

```bash
# Generate llms.txt
curl -X POST "https://your-app.vercel.app/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.anthropic.com", 
    "max_pages": 20,
    "depth_limit": 3
  }'

# Monitoring endpoints
curl -X POST "https://your-app.vercel.app/api/scheduler" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add_site",
    "url": "https://docs.anthropic.com",
    "max_pages": 20,
    "check_interval": 86400
  }'
```

## 🔧 Configuration

### Environment Variables

#### Required Setup
```env
# For local development (.env)
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI API key for AI enhancement (required)
OPENAI_API_KEY=your_openai_api_key_here
```

#### Production (Vercel Dashboard)
```env
OPENAI_API_KEY=your_openai_api_key_here
# NEXT_PUBLIC_API_URL automatically detected
```

### Application Settings

#### Crawler Configuration
- `max_pages`: Maximum number of pages to crawl (default: 20)
- `depth_limit`: Maximum crawl depth from the root URL (default: 3)
- `check_interval`: Monitoring interval in seconds (default: 86400 = 24 hours)

#### AI Enhancement Features
When OpenAI API key is provided:
- **Enhanced Descriptions**: AI-improved page descriptions
- **Smart Categorization**: Dynamic section organization
- **Content Cleanup**: Removes redundancy and improves clarity
- **Scalable Processing**: Adjusts AI usage based on website size

### Monitoring Best Practices

#### Site Selection
- **Documentation sites**: Perfect for monitoring (docs.*, developers.*)
- **News sites**: Good for content updates (moderate frequency)
- **Large sites**: Use smaller page limits (10-20 pages)

#### Interval Recommendations
- **Critical docs**: Every 6-12 hours
- **Regular updates**: Daily (24 hours) - **Recommended**
- **Stable sites**: Every 3 days
- **Archive sites**: Weekly

#### Performance Optimization
- **Small crawls (≤20 pages)**: Full AI enhancement
- **Medium crawls (21-50 pages)**: AI with 8 pages max per section
- **Large crawls (51-100 pages)**: AI limited to 5 pages per section
- **Very large crawls (>100 pages)**: No AI enhancement (prevents timeouts)

## 🚢 Deployment

### Production Deployment with Vercel

The project includes automated deployment to Vercel with cron job scheduling.

**Quick Deploy:**
```bash
./deploy-vercel.sh
```

**Manual Deploy:**
```bash
# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

**⚠️ Important Notes:**
- **Vercel Free Plan**: Function timeout limited to 60 seconds max, **cron jobs limited to daily frequency**
- **Vercel Pro Plan**: Function timeout can be up to 300 seconds, **unlimited cron frequency** 
- For large websites (>50 pages), consider upgrading to Pro plan or use local development
- **Free plan**: Cron jobs run daily at 12:00 PM UTC
- **Pro plan**: Can run every 6 hours or any custom schedule

**Environment Variables Required:**
```bash
# Set in Vercel dashboard or via CLI
vercel env add OPENAI_API_KEY
```

### Vercel Configuration

The `vercel.json` includes:
```json
{
  "functions": {
    "api/generate.py": { "maxDuration": 300 },
    "api/scheduler.py": { "maxDuration": 600 },
    "api/cron.py": { "maxDuration": 900 }
  },
  "crons": [
    {
      "path": "/api/cron",
      "schedule": "0 */6 * * *"
    }
  ]
}
```

## 🧪 Testing

### Test Local Development
```bash
# Test main API
curl http://localhost:8000/health

# Test scheduler API  
curl http://localhost:8001/cron

# Test frontend
open http://localhost:3000
```

### Test Production Deployment
```bash
# Test Vercel functions
curl https://your-app.vercel.app/api/health

# Test monitoring dashboard
open https://your-app.vercel.app/monitor
```

## 📊 Understanding Change Detection

### Change Types Detected
- **New pages**: Recently added documentation or content
- **Removed pages**: Deleted or moved content
- **Modified pages**: Title changes, section reassignments
- **Structural changes**: Navigation reorganization, new product areas

### Severity Levels
- **Major (50%+)**: Large restructures, new product launches → Always update
- **Moderate (20%+)**: New documentation sections → Always update
- **Minor (5%+)**: New pages, title changes → Always update
- **Minimal (<5%)**: Minor tweaks → Skip update (prevents noise)

### Example Change Report
```json
{
  "severity": "moderate",
  "new_pages": [
    "https://docs.example.com/new-api-guide",
    "https://docs.example.com/beta-features"
  ],
  "removed_pages": [
    "https://docs.example.com/deprecated-api"
  ],
  "modified_pages": [
    {
      "url": "https://docs.example.com/quickstart",
      "old_title": "Quick Start",
      "new_title": "Getting Started Guide",
      "old_section": "Documentation",
      "new_section": "Getting Started"
    }
  ]
}
```

## ⚡ Performance & Scaling

### Vercel Function Limits
- **Execution Time**: 10 seconds (Hobby), 60 seconds (Pro), 900 seconds (cron)
- **Memory**: Up to 1024MB
- **Payload Size**: 4.5MB request/response limit

### Monitoring Efficiency
- **Concurrent checks**: System handles multiple sites efficiently
- **Smart scheduling**: Only checks sites when intervals are due
- **Change thresholds**: Prevents unnecessary regeneration
- **Timeout management**: Graceful degradation for large sites

### Scaling Tips
- **Use appropriate page limits**: See [Configuration](#-configuration) for recommendations
- **Monitor function execution times**: Check Vercel dashboard for performance metrics
- **Consider Pro plan**: For larger sites requiring longer execution times
- **Batch monitoring**: System automatically batches multiple site checks efficiently

## 🐛 Troubleshooting

### Common Issues

**"Failed to fetch" errors locally:**
- Check that `.env` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Ensure backend servers are running on ports 8000 and 8001

**"Site not being monitored":**
- Add the site first using the monitor interface
- Check the URL format (include https://)

**"No changes detected but site updated":**
- Check if changes are below 5% threshold
- Force manual check to see latest status
- Consider if changes are in content vs. structure

**"Update failed":**
- Check if the website is accessible
- Verify the site doesn't block crawlers
- Look for SSL/security issues

### Debug Mode
```bash
export DEBUG=1
export LOG_LEVEL=DEBUG
python run_dev.py
```

## 🚀 Future Enhancements

### Planned Features
- **Database persistence**: Store monitoring data permanently
- **Email notifications**: Alert when sites update
- **Webhook integration**: Push updates to external systems
- **Advanced scheduling**: Per-site custom schedules
- **Change analytics**: Track patterns and trends
- **Team collaboration**: Shared monitoring dashboards

### Contributing Areas
- `ChangeDetector`: Improve change detection algorithms
- `AutoUpdater`: Add new notification methods
- `LLMSTxtGenerator`: Enhance content organization
- Frontend: Better visualization and management tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Test locally with `python run_dev.py`
4. Test monitoring features on `/monitor` page
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Jeremy Howard](https://github.com/jph00) for proposing the llms.txt standard
- [llmstxt.org](https://llmstxt.org/) for the specification
- The open source community for the amazing tools used in this project

## 📞 Support

If you encounter any issues or have questions:

1. Check this README for common solutions
2. Review the API documentation at `/docs` endpoints (local development)
3. Create an issue with detailed information
4. Include error messages and steps to reproduce
5. Mention whether you're running locally or on Vercel

---

## 📋 Quick Reference

### Local URLs
- **Main App**: http://localhost:3000
- **Monitor Dashboard**: http://localhost:3000/monitor
- **Main API Docs**: http://localhost:8000/docs
- **Scheduler API Docs**: http://localhost:8001/docs

### Key Commands
```bash
# Start development (automated script - recommended)
./start.sh

# Start development (convenience script)
cd backend && python run_dev.py

# Deploy to production (automated script - recommended)
./deploy-vercel.sh

# Deploy to production (manual)
vercel --prod

# Test APIs locally
curl http://localhost:8000/health
curl http://localhost:8001/cron

# Add site to monitoring
# Visit /monitor page or use API directly
```

### Environment Variables
```env
# Local development (.env)
NEXT_PUBLIC_API_URL=http://localhost:8000
OPENAI_API_KEY=your_openai_api_key_here

# Production (Vercel Dashboard)
OPENAI_API_KEY=your_openai_api_key_here
```

## ⏰ Automated Monitoring Setup

### Production Setup (Vercel) - Automatic

**Good News**: Cron jobs are automatically configured when you deploy to Vercel! 🎉

1. **Deploy to Vercel** (using either method above)
   ```bash
   ./deploy-vercel.sh  # or vercel --prod
   ```

2. **Cron jobs are automatically enabled:**
   - ✅ **Free Plan**: Runs daily at 12:00 PM UTC (`0 12 * * *`)
   - ✅ **Pro Plan**: Can run every 6 hours (`0 */6 * * *`) or custom schedule
   - ✅ Checks all monitored sites for changes
   - ✅ Updates llms.txt files when significant changes detected
   - ✅ 60-second execution limit (Free) or 300+ seconds (Pro)

3. **Verify cron is working:**
   ```bash
   # Check cron endpoint manually
   curl https://your-app.vercel.app/api/cron
   
   # Check Vercel dashboard
   # Go to: Project → Functions → View function logs
   ```

4. **Monitor cron activity:**
   - Visit your app's `/monitor` page
   - Check "Last Update" timestamps
   - Look for "Auto-updated" entries in the monitoring dashboard

### Local Development Setup

For local development, you can simulate cron behavior:

**Option A: Manual cron trigger**
```bash
# Trigger cron check manually
curl http://localhost:8001/cron

# Or visit in browser
open http://localhost:8001/cron
```

**Option B: Set up local cron (macOS/Linux)**
```bash
# Edit your crontab
crontab -e

# Add this line to run every hour during development
0 * * * * curl -s http://localhost:8001/cron >/dev/null 2>&1

# Or every 6 hours to match production
0 */6 * * * curl -s http://localhost:8001/cron >/dev/null 2>&1
```

**Option C: Use a cron service**
```bash
# Install a cron alternative like 'node-cron' for local development
npm install node-cron

# Create a simple Node.js script for local cron
cat > local-cron.js << 'EOF'
const cron = require('node-cron');
const fetch = require('node-fetch');

// Run every 6 hours
cron.schedule('0 */6 * * *', async () => {
  try {
    const response = await fetch('http://localhost:8001/cron');
    console.log(`Cron job completed: ${response.status}`);
  } catch (error) {
    console.error('Cron job failed:', error);
  }
});

console.log('Local cron scheduler started...');
EOF

# Run the local cron scheduler
node local-cron.js
```

### Understanding Cron Schedule

**Vercel Free Plan Schedule: `0 12 * * *`**
```
┌───────────── minute (0)
│ ┌─────────── hour (12 = 12:00 PM UTC)
│ │ ┌───────── day of month (*)
│ │ │ ┌─────── month (*)
│ │ │ │ ┌───── day of week (*)
│ │ │ │ │
│ │ │ │ │
0 12 * * *
```

**This means:**
- **12:00 PM UTC daily** (4 AM or 5 AM Pacific, depending on DST)

**Vercel Pro Plan Schedule: `0 */6 * * *`**
```
┌───────────── minute (0)
│ ┌─────────── hour (*/6 = every 6 hours)
│ │ ┌───────── day of month (*)
│ │ │ ┌─────── month (*)
│ │ │ │ ┌───── day of week (*)
│ │ │ │ │
│ │ │ │ │
0 */6 * * *
```

**This means:**
- **12:00 AM UTC** (4 PM or 5 PM Pacific, depending on DST)
- **6:00 AM UTC** (10 PM or 11 PM Pacific)
- **12:00 PM UTC** (4 AM or 5 AM Pacific)
- **6:00 PM UTC** (10 AM or 11 AM Pacific)

### Customizing Cron Schedule

⚠️ **Vercel Plan Limitations:**
- **Free (Hobby) Plan**: Only daily schedules allowed (e.g., `0 12 * * *`)
- **Pro Plan**: Any schedule frequency supported

To change the monitoring frequency, edit `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/cron",
      "schedule": "0 0 * * *"    // Daily at midnight UTC (Free plan compatible)
    }
  ]
}
```

**Free plan compatible schedules:**
- `0 0 * * *` - Daily at midnight UTC
- `0 12 * * *` - Daily at noon UTC (default)
- `0 6 * * *` - Daily at 6 AM UTC
- `0 0 * * 1` - Weekly on Mondays

**Pro plan additional schedules:**
- `0 */1 * * *` - Every hour
- `0 */2 * * *` - Every 2 hours  
- `0 */6 * * *` - Every 6 hours
- `0 */12 * * *` - Every 12 hours

**After changing the schedule:**
```bash
# Redeploy to apply changes
vercel --prod
```

### Troubleshooting Cron Jobs

**Cron not running:**
```bash
# 1. Check if cron endpoint works manually
curl https://your-app.vercel.app/api/cron

# 2. Check Vercel function logs
# Visit Vercel Dashboard → Project → Functions → api/cron.py

# 3. Verify vercel.json syntax
cat vercel.json | python -m json.tool
```

**No sites being checked:**
- Make sure you've added sites to monitoring via `/monitor` page
- Check that sites have valid URLs (include https://)
- Verify OpenAI API key is set in Vercel environment variables

**Cron running but not updating:**
- Changes might be below 5% threshold (prevents noise)
- Check the specific site manually: force update via `/monitor` page
- Look at function logs for error messages

### Monitoring Cron Activity

**In the app:**
1. Visit `/monitor` page
2. Look for "Last Update" column
3. Check for recent timestamps
4. Look for "Auto-updated" vs "Manual" in update history

**In Vercel Dashboard:**
1. Go to your project
2. Click "Functions" tab
3. Click on `api/cron.py`
4. View execution logs and duration

**Expected behavior:**
- Cron runs every 6 hours
- Only updates sites with significant changes (5%+)
- Updates multiple sites efficiently in single execution
- Completes within 15-minute timeout limit 

Built with ❤️ for the llms.txt standard and automated monitoring!