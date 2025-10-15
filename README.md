# 🚀 LLMs.txt Generator - Self-Hosted & Open Source

> **"Let the LLMs eat your content!"** - Open source **llms.txt generator** for **AI content optimization**. Self-hosted solution with automated bi-weekly generation, sitemap-first crawling, and FAQ extraction. Boost citations in ChatGPT, Perplexity, and Gemini!

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](./DOCKER_SETUP.md)
[![Systemd](https://img.shields.io/badge/Systemd-Supported-green.svg)](./SYSTEMD_SETUP.md)

An intelligent web application that generates `llms.txt` files for websites with **automated bi-weekly updates**. This tool follows the [llms.txt specification](https://llmstxt.org/) to create AI-friendly documentation that helps Large Language Models better understand your content.

**🌟 Key Features:**
- 🖥️ **Self-Hosted** - Run on your own server, no cloud dependencies
- ⏰ **Automated** - Bi-weekly generation with cron jobs
- 🗺️ **Sitemap-First** - Complete website coverage
- 📋 **FAQ Extraction** - Schema.org markup support
- 🐳 **Docker Ready** - One-command deployment
- 🔧 **Systemd Support** - Native Linux service integration

## 📋 Table of Contents

### 🚀 Quick Start
- [✨ Features](#-features)
- [⚡ Quick Installation](#-quick-installation)
- [🎬 Quick Demo](#-quick-demo)

### 📦 Deployment Options
- [🐳 Docker Deployment](#-docker-deployment)
- [⚙️ Systemd Services](#️-systemd-services)
- [💻 Local Development](#-local-development)

### ⏰ Automation
- [🔄 Bi-Weekly Generation](#-bi-weekly-generation)
- [📊 Monitoring](#-monitoring)
- [🌐 Public Access](#-public-access)

### 📚 Documentation
- [🔧 Configuration](#-configuration)
- [🐛 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)

## ✨ Features

### Core Generation & LLM SEO
- **🗺️ Sitemap-First Crawling**: Automatically discovers ALL pages via sitemap.xml/sitemap_index.xml for complete **AI content optimization**
- **📋 FAQ Extraction for Semantic SEO**: Extracts FAQs from Schema.org JSON-LD markup - perfekt für **semantic SEO** und **AEO (Answer Engine Optimization)** – extrahiert Q&A für AI-Responses
- **🎯 Two-Stage Workflow**: Generate summary first, then full-text with all pages optimized for **LLM search optimization**
- **🚀 LLM SEO Boost**: Optimiere für **Generative Engine Optimization (GEO)** – erhöhe Citations in ChatGPT/Perplexity durch strukturierte FAQs und Semantics
- **AI-Enhanced Content**: Uses OpenAI to improve descriptions and organization for better **AI visibility**
- **Smart Categorization**: Dynamic section organization based on content themes using **topic clustering** for LLMs
- **Dual File Generation**: Creates both `llms.txt` (curated for **GEO**) and `llms-full.txt` (comprehensive **semantic SEO** coverage)
- **Existing File Detection**: Automatically uses existing llms.txt files when found

### Self-Hosted & Automation
- **🖥️ Self-Hosted**: Run on your own server - Docker, Systemd, or manual
- **⏰ Automated Generation**: Bi-weekly cron jobs for fresh content
- **🔄 Multi-Website Support**: Generate for multiple domains simultaneously
- **📦 Local & Remote Deployment**: Copy files locally or deploy via SCP
- **💚 Health Monitoring**: Auto-restart on failures
- **📧 Notifications**: Email and Slack alerts (optional)

### Modern Interface
- **Beautiful UI**: Responsive design built with Next.js and Tailwind CSS
- **Real-time Progress**: Live feedback during crawling and generation
- **Instant Downloads**: Direct download of generated files
- **Public Access**: Share with your team via Nginx

## ⚡ Quick Installation

### Option 1: Docker (Recommended - 2 Minutes)

```bash
# Clone repository
git clone https://github.com/obviousworks/ai-llmstxt-generator.git
cd ai-llmstxt-generator/llm_txt_creator

# Configure
cp env.example .env
nano .env  # Add your OPENAI_API_KEY

# Start
docker-compose up -d

# Access at http://localhost:3000
```

**Done!** See [DOCKER_SETUP.md](./DOCKER_SETUP.md) for details.

### Option 2: Systemd Services (5 Minutes)

```bash
# Clone repository
git clone https://github.com/obviousworks/ai-llmstxt-generator.git
cd ai-llmstxt-generator/llm_txt_creator

# Install as system service
sudo ./systemd/install.sh

# Access at http://localhost:3000
```

**Done!** See [SYSTEMD_SETUP.md](./SYSTEMD_SETUP.md) for details.

### Option 3: Local Development

```bash
# Clone repository
git clone https://github.com/obviousworks/ai-llmstxt-generator.git
cd ai-llmstxt-generator/llm_txt_creator

# Setup backend
cd backend
pip install -r requirements.txt
python run_dev.py &

# Setup frontend (new terminal)
cd ..
npm install
npm run dev

# Access at http://localhost:3000
```

## 🎬 Quick Demo

### Try It in 30 Seconds
```bash
# After installation, open browser
http://localhost:3000

# Enter a website URL (e.g., https://obviousworks.ch)
# Click "Generate llms.txt (Summary)" for quick overview
# Click "Generate llms-full.txt (All Pages)" for complete documentation ✨
```

### What You'll See
1. **Sitemap discovery**: Automatically finds and parses sitemap_index.xml
2. **Complete crawling**: All pages from sitemap analyzed (e.g., 296 pages in 39 seconds)
3. **FAQ extraction**: Automatically extracts FAQs from Schema.org markup
4. **Real-time progress**: Pages discovered and analyzed live with progress indicators
5. **AI enhancement**: Content improved and categorized automatically  
6. **Dual outputs**: Both curated summary and comprehensive full-text versions
7. **FAQ indicators**: Pages with FAQs marked with [📋 X FAQs] in summary

### Example Output

**llms.txt (Summary):**
```markdown
# obviousworks.ch

## Schulungen
- [Certified Agile Requirements Specialist (CARS)](https://...): CARS Zertifizierung für agiles Requirements Engineering [📋 19 FAQs]
- [Certified Professional for Requirements Engineering (CPRE)](https://...): Internationale IREB Zertifizierung

## Dienstleistungen
- [Requirements Engineering Services](https://...): Professionelle Unterstützung für Ihre Projekte
...
```

**llms-full.txt (Complete):**
```markdown
## Certified Agile Requirements Specialist (CARS)

URL: https://www.obviousworks.ch/schulungen/certified-agile-requirements-specialist-cars/

### FAQs (19 questions)

**Q: Was ist der Certified Agile Requirements Specialist (CARS)?**

A: Der Certified Agile Requirements Specialist (CARS) ist eine Zertifizierung, die fundierte Kenntnisse...

**Q: Was sind die Hauptinhalte des CARS-Trainings?**

A: Das CARS-Training deckt eine Vielzahl von Themen ab, darunter: Grundlagen des Requirements Engineering...
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

## 🆕 Recent Improvements & Features

### Sitemap-First Crawling Strategy
The crawler now prioritizes sitemap discovery for complete website coverage:

1. **Sitemap Discovery Chain**:
   - Checks `robots.txt` for sitemap location
   - Tries common locations: `sitemap_index.xml`, `sitemap.xml`, etc.
   - Recursively parses sitemap indexes and sub-sitemaps
   - Falls back to link-based crawling if no sitemap found

2. **Benefits**:
   - ✅ Discovers ALL pages (no depth limit issues)
   - ✅ Faster crawling (direct URL list)
   - ✅ More reliable (no missed pages)
   - ✅ Example: 296 pages from obviousworks.ch in 39 seconds

### FAQ Extraction from Schema.org
Automatically extracts structured FAQ data from JSON-LD markup:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Your question here?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Your answer here"
      }
    }
  ]
}
</script>
```

**Features**:
- Extracts all Q&A pairs from FAQPage schema
- Includes FAQs in `llms-full.txt` with dedicated section
- Marks pages with FAQs in summary: `[📋 X FAQs]`
- Boosts importance score for FAQ-rich pages (+0.02 per FAQ, max +0.3)

### Two-Stage Generation Workflow
New UI with separate buttons for different use cases:

1. **Generate llms.txt (Summary)** - Blue Button
   - Quick overview with most important pages
   - Adaptive filtering based on crawl size
   - For 296 pages: includes pages with score > 0.15
   - AI enhancement for key sections

2. **Generate llms-full.txt (All Pages)** - Green Button
   - Complete documentation with ALL crawled pages
   - Includes full FAQ sections
   - No filtering or limits
   - Perfect for comprehensive LLM context

### Adaptive Content Filtering
Smart thresholds based on website size:

| Pages Crawled | Importance Threshold | Pages per Section |
|---------------|---------------------|-------------------|
| ≤ 50          | > 0.3               | All important     |
| 51-100        | > 0.2               | All important     |
| 101-200       | > 0.15              | All important     |
| 200+          | > 0.1               | All important     |

**No more artificial limits** - all important pages are included!

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

## 🐳 Docker Deployment

Complete Docker setup with production-ready configuration.

**Quick Start:**
```bash
# Clone and configure
git clone https://github.com/obviousworks/ai-llmstxt-generator.git
cd ai-llmstxt-generator/llm_txt_creator
cp env.example .env
nano .env  # Add OPENAI_API_KEY

# Start
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

**Features:**
- ✅ Multi-stage build for optimized image size
- ✅ Health checks for both services
- ✅ Volume mounts for generated files and logs
- ✅ Automatic restart policy
- ✅ Production-ready configuration

**See [DOCKER_SETUP.md](./DOCKER_SETUP.md) for complete guide.**

## ⚙️ Systemd Services

Run as native Linux services with automatic startup.

**Quick Start:**
```bash
# Clone repository
git clone https://github.com/obviousworks/ai-llmstxt-generator.git
cd ai-llmstxt-generator/llm_txt_creator

# Install
sudo ./systemd/install.sh

# Manage services
sudo systemctl status llms-api llms-frontend
sudo systemctl restart llms-api llms-frontend
sudo journalctl -u llms-api -f
```

**Features:**
- ✅ Auto-start on boot
- ✅ Automatic restart on failure
- ✅ Proper logging to `/var/log/llms-generator/`
- ✅ Security hardening
- ✅ Service dependencies

**See [SYSTEMD_SETUP.md](./SYSTEMD_SETUP.md) for complete guide.**

## 💻 Local Development

For development and testing.

**Setup:**
```bash
# Backend
cd backend
pip install -r requirements.txt
python run_dev.py  # Runs on port 8000

# Frontend (new terminal)
npm install
npm run dev  # Runs on port 3000
```

**Environment:**
```bash
# Create .env file
cp env.example .env

# Add your API key
OPENAI_API_KEY=your_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🔄 Bi-Weekly Generation

Automate llms.txt generation for multiple websites.

**Quick Setup:**
```bash
# 1. Configure websites
nano config/websites.conf

# Add your websites
WEBSITES=(
    "https://your-website.com"
    "https://another-site.com"
)

DEPLOY_TARGETS=(
    ["your-website.com"]="/var/www/your-site/public"
    ["another-site.com"]="user@server:/var/www/html"
)

# 2. Test scripts
./scripts/generate-llms.sh
./scripts/deploy-llms.sh

# 3. Setup cron (every 2 weeks)
./scripts/setup-cron.sh
```

**Features:**
- ✅ Bi-weekly automated generation
- ✅ Multi-website support
- ✅ Local and remote deployment (SCP)
- ✅ Automatic retry on failure
- ✅ Email/Slack notifications
- ✅ Health monitoring

**See [AUTOMATION_SETUP.md](./AUTOMATION_SETUP.md) for complete guide.**

## 📊 Monitoring

Monitor services and automate health checks.

**Health Check:**
```bash
# Manual check
./scripts/health-check.sh

# Automated (add to cron)
*/5 * * * * /path/to/scripts/health-check.sh
```

**View Logs:**
```bash
# Generation logs
tail -f /var/log/llms-generator.log

# Service logs (Docker)
docker-compose logs -f

# Service logs (Systemd)
sudo journalctl -u llms-api -f
sudo journalctl -u llms-frontend -f
```

**Statistics:**
```bash
# Count successful generations
grep "✅ Success" /var/log/llms-generator.log | wc -l

# View last generation summary
grep "Generation Summary" -A 5 /var/log/llms-generator.log | tail -6
```

## 🌐 Public Access

Share with your team using Nginx reverse proxy.

**Quick Setup:**
```bash
# Install Nginx configuration
sudo ./nginx/install.sh

# Enter your domain when prompted
# Example: llms-generator.your-domain.com
```

**Enable HTTPS:**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d llms-generator.your-domain.com

# Auto-renewal is configured automatically
```

**Features:**
- ✅ HTTP to HTTPS redirect
- ✅ SSL/TLS configuration
- ✅ Security headers
- ✅ Gzip compression
- ✅ WebSocket support
- ✅ Proper timeouts for API generation

## 🐛 Troubleshooting

### Docker Issues

**Container won't start:**
```bash
# Check logs
docker-compose logs

# Check if ports are available
sudo lsof -i :8000
sudo lsof -i :3000

# Rebuild
docker-compose down
docker-compose up -d --build
```

**Backend not responding:**
```bash
# Check backend health
curl http://localhost:8000/health

# View backend logs
docker-compose exec llms-generator cat /app/logs/backend.log
```

### Systemd Issues

**Services won't start:**
```bash
# Check service status
sudo systemctl status llms-api llms-frontend

# Check logs
sudo journalctl -u llms-api -n 50
sudo journalctl -u llms-frontend -n 50

# Test manually
cd /opt/llms-generator/backend
python3 run_dev.py
```

**Permission denied:**
```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/llms-generator
sudo chown -R www-data:www-data /var/log/llms-generator
```

### Automation Issues

**Generation fails:**
```bash
# Check API is running
curl http://localhost:8000/health

# Test generation manually
./scripts/generate-llms.sh

# Check logs
tail -f /var/log/llms-generator.log
```

**Cron not running:**
```bash
# Check cron service
sudo systemctl status cron

# Verify cron job
crontab -l

# Test manually
./scripts/generate-llms.sh && ./scripts/deploy-llms.sh
```

### Common Issues

**"Failed to fetch" errors:**
- Check `.env` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Ensure backend is running on port 8000
- Verify firewall allows connections

**"OpenAI API error":**
- Check API key is set correctly
- Verify API key has credits
- Check OpenAI service status

**"Deployment failed":**
- Check SSH keys for remote deployment
- Verify target directories exist
- Check permissions on target paths

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_key_here

# Optional
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=https://your-domain.com
```

### Website Configuration

Edit `config/websites.conf`:

```bash
# Websites to generate for
WEBSITES=(
    "https://your-website.com"
)

# Generation settings per domain
declare -A GENERATION_SETTINGS=(
    ["your-website.com"]="50"  # Max pages
)

# Deployment targets
declare -A DEPLOY_TARGETS=(
    ["your-website.com"]="/var/www/your-site/public"
)

# Schedule (every 2 weeks)
CRON_SCHEDULE="0 2 */14 * *"
```

## 🎯 Future Development

This fork is actively maintained by ObviousWorks. Future features will be documented here with implementation dates.

**Planned Features für LLM SEO 2025:**
- [ ] **GEO/AEO Integration**: Automatische Schema-Markup-Generierung für **LLM search optimization**
- [ ] Multi-Modal Support: Optimiere für Video/Infographics in AI-Suchen
- [ ] Multi-language support for FAQ extraction
- [ ] Enhanced AI categorization with custom prompts für **topic clustering**
- [ ] Batch processing for multiple websites
- [ ] Export to additional formats (JSON, XML)
- [ ] Advanced analytics dashboard mit **AI visibility metrics**
- [ ] Webhook integration for deployment notifications
- [ ] Database persistence for generation history

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

## 📝 Changelog

> **Note**: All features are documented with implementation dates for tracking and reference.

---

### Version 2.2.0 - Existing Files Detection & Regeneration
**Release Date: October 10, 2025**

#### 🚀 New Features
- **Existing Files Detection**: Automatically detects existing llms.txt and llms-full.txt files
  - Checks both root directory and .well-known/ locations
  - Shows user-friendly dialog when existing files are found
  - Lists all detected files with clear options
- **Regeneration Choice**: User can choose to generate new files or cancel
  - "Generate New Summary" button for llms.txt regeneration
  - "Generate New Full-Text" button for llms-full.txt regeneration
  - "Cancel" option to keep existing files
- **Enhanced Backend**: Added `force_regenerate` parameter to API
  - Prevents automatic stopping when existing files detected
  - Improved user control over generation process

---

### Version 2.1.1 - UTF-8 BOM Fix for Browser Compatibility
**Release Date: October 10, 2025**

#### 🐛 Bug Fixes
- **UTF-8 BOM**: Added Byte Order Mark to downloaded files for browser compatibility
  - Fixes umlauts display issues when opening files in browsers
  - Prevents garbled text like `fÃ¼r` → `für` in browser-opened files
  - Files opened in text editors (vi, nano, etc.) remain unaffected
  - Improves user experience for browser-based file viewing

---

### Version 2.1.0 - Help System & User Guidance
**Release Date: October 10, 2025**

#### 🚀 New Features
- **Comprehensive Help Page**: Added `/help` route with detailed setup instructions
  - Complete AI features explanation and benefits
  - Step-by-step OpenAI API key setup for local and production
  - Monitoring system documentation and limitations
  - Clear guidance on what works with/without AI enhancement
- **Enhanced Navigation**: Added help link to main page header
- **User Onboarding**: Clear documentation for new users

---

### Version 2.0.1 - UTF-8 Encoding Fix
**Release Date: October 10, 2025**

#### 🐛 Bug Fixes
- **UTF-8 Encoding**: Fixed umlauts and special characters encoding issues
  - Set explicit UTF-8 encoding for all HTTP responses
  - Fixed BeautifulSoup parsing with UTF-8 encoding
  - Ensured download files use UTF-8 charset
  - Prevents garbled text like `FÃ¤higkeiten` → `Fähigkeiten`
  - Affects: Page content, FAQ extraction, sitemap parsing, file downloads

---

### Version 2.0.0 - ObviousWorks Enhanced Fork
**Release Date: October 7, 2025**

#### 🚀 Major Features Added
- **Sitemap-First Crawling**: Complete website coverage via sitemap.xml/sitemap_index.xml
  - Automatically discovers and parses sitemap indexes
  - Recursively fetches all sub-sitemaps
  - Falls back to link-based crawling if no sitemap found
  - Example: 296 pages crawled from obviousworks.ch in 39 seconds

- **FAQ Extraction**: Schema.org JSON-LD support
  - Extracts FAQs from FAQPage markup
  - Includes Q&A pairs in llms-full.txt
  - Marks pages with FAQ indicator in summary: `[📋 X FAQs]`
  - Boosts importance score for FAQ-rich pages

- **Two-Stage Workflow**: Separate generation modes
  - Blue button: Generate llms.txt (Summary) - curated overview
  - Green button: Generate llms-full.txt (All Pages) - complete documentation
  - Independent generation with separate loading states

#### 🔧 Improvements
- **Adaptive Content Filtering**: Smart thresholds based on website size
  - 200+ pages: includes pages with score > 0.1
  - 101-200 pages: includes pages with score > 0.15
  - 51-100 pages: includes pages with score > 0.2
  - ≤50 pages: includes pages with score > 0.3

- **No More Artificial Limits**: Removed per-section page limits
  - All important pages are now included
  - Better coverage for large websites
  - More comprehensive documentation

- **Enhanced UI**: Improved user experience
  - Separate buttons for summary and full-text generation
  - Clear progress indicators for each mode
  - FAQ count displayed in page listings
  - Better error handling and messaging

#### 🐛 Bug Fixes
- Fixed depth limit issue preventing complete crawls
- Fixed page filtering that excluded too many pages
- Improved sitemap parsing for various formats
- Better handling of large website crawls (200+ pages)

#### 📚 Documentation
- Updated README with new features and examples
- Added sitemap crawling strategy documentation
- Added FAQ extraction examples
- Added adaptive filtering table
- Updated quick start guide with new workflow

---

### Version 1.0.0 - Base Fork
**Release Date: October 2025**

Forked from [rdyplayerB/ai-llmstxt-generator](https://github.com/rdyplayerB/ai-llmstxt-generator) with the following base features:
- Basic website crawling with link following
- AI-enhanced content generation
- Dual file generation (llms.txt and llms-full.txt)
- Automated monitoring with change detection
- Next.js frontend with Tailwind CSS
- FastAPI backend with OpenAI integration

---

## 🎯 Future Development

This fork is actively maintained by ObviousWorks. Future features will be documented here with implementation dates.

**Planned Features für LLM SEO 2025:**
- [ ] **GEO/AEO Integration**: Automatische Schema-Markup-Generierung für **LLM search optimization**
- [ ] Multi-Modal Support: Optimiere für Video/Infographics in AI-Suchen
- [ ] Multi-language support for FAQ extraction
- [ ] Enhanced AI categorization with custom prompts für **topic clustering**
- [ ] Batch processing for multiple websites
- [ ] Export to additional formats (JSON, XML)
- [ ] Advanced analytics dashboard mit **AI visibility metrics**

---

## 🏢 About ObviousWorks

**ObviousWorks** is Switzerland's leading expert in Requirements Engineering (IREB®), Agile methodologies, and AI/LLM integration for software development. We bridge the gap between traditional software engineering and the AI-powered future.

### 🧠 Our AI & LLM Training Programs
- **[AI Masterclass](https://www.obviousworks.ch/schulungen/ai-masterclass/)** - Perfect introduction to generative AI
- **[ChatGPT 101 for Beginners](https://www.obviousworks.ch/schulungen/chatgpt-101/)** - Save hours of work with AI
- **[Getting Started with Generative AI](https://www.obviousworks.ch/schulungen/generative-ai-getting-started/)** - Boost productivity with AI tools
- **[ChatGPT Coding](https://www.obviousworks.ch/schulungen/chatgpt-coding/)** - AI-powered development workflows
- **[ChatGPT Advanced](https://www.obviousworks.ch/schulungen/chatgpt-advanced/)** - Enterprise-grade LLM integration
- **[Generative AI for Software Development](https://www.obviousworks.ch/schulungen/generative-ai-fuer-effiziente-softwareentwicklung/)** - Full-stack AI implementation
- **[AI Requirements Engineering](https://www.obviousworks.ch/schulungen/ai-requirements-engineering/)** - RE in AI-driven environments
- **[AI Developer Bootcamp](https://www.obviousworks.ch/schulungen/ai-developer-bootcamp/)** - End-to-end AI development lifecycle

### 🎓 Certification Programs
- **[IREB® CPRE with AI Modules](https://www.obviousworks.ch/schulungen/ireb-cpre-foundation/)** - Requirements Engineering certification
- **[CARS® with AI Prioritization](https://www.obviousworks.ch/schulungen/agile-requirements-specialist/)** - Agile Requirements Specialist

### 🔗 Connect With Us
- **Website**: [obviousworks.ch](https://www.obviousworks.ch/)
- **GitHub**: [github.com/obviousworks](https://github.com/obviousworks)
- **Services**: AI Transformation Implementation, Enterprise LLM Integration

---

## 🚀 Get Started Now!

**Starte deinen llms.txt generator jetzt – booste AI search visibility!** 

⭐ **Star this Repo** für Updates zu **LLM SEO 2025** trends  
🔗 **Try it live**: [Free LLMs.txt Generator](https://llm-txt-generator.vercel.app)  
📚 **Learn more**: [LLM SEO Training bei ObviousWorks](https://obviousworks.ch)

Built with ❤️ by [ObviousWorks](https://obviousworks.ch) for the **llms.txt standard** and **AI visibility optimization**.

**Original Project**: [rdyplayerB/ai-llmstxt-generator](https://github.com/rdyplayerB/ai-llmstxt-generator)