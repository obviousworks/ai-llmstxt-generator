# LLMs.txt Generator

An automated tool that generates `llms.txt` files for websites by analyzing their structure and content. This tool follows the [llms.txt specification](https://llmstxt.org/) to create AI-friendly documentation files that help Large Language Models better understand website content.

## 🚀 Features

- **Intelligent Website Crawling**: Automatically discovers and analyzes website pages
- **Content Scoring**: Uses importance algorithms to prioritize key content
- **Section Categorization**: Automatically organizes content into logical sections
- **Dual File Generation**: Creates both `llms.txt` (curated) and `llms-full.txt` (comprehensive)
- **Modern Web Interface**: Beautiful, responsive UI built with Next.js and Tailwind CSS
- **Serverless Backend**: Python functions deployed on Vercel for scalable processing
- **Real-time Progress**: Live feedback during crawling and generation
- **Instant Downloads**: Direct download of generated files

## 🛠 Technology Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Modern styling
- **Lucide React** - Beautiful icons

### Backend
- **Vercel Functions** - Serverless Python functions
- **aiohttp** - Async HTTP client for web crawling
- **BeautifulSoup4** - HTML parsing and content extraction

## 📦 Installation & Setup

### Prerequisites
- **Node.js 18+** (for frontend)
- **Python 3.9+** (for local backend development)
- **npm or yarn** (package manager)
- **Vercel CLI** (for deployment)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd llm-txt-generator
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start local development (recommended)**
   
   **Use the automated start script:**
   ```bash
   ./start.sh
   ```
   This script automatically:
   - Sets up Python virtual environment
   - Installs backend dependencies  
   - Starts both backend (port 8000) and frontend (port 3000)
   
   **Manual setup (alternative):**
   
   Set up local backend:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
   
   Start services in separate terminals:
   
   Terminal 1 (Backend):
   ```bash
   cd backend
   source venv/bin/activate
   python main.py
   ```
   
   Terminal 2 (Frontend):
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

## 🎯 Usage

### Web Interface

1. **Enter Website URL**: Input the URL you want to analyze
2. **Configure Settings**: Choose maximum pages to crawl (10-100)
3. **Generate Files**: Click "Generate llms.txt" and wait for processing
4. **Download Results**: Download both `llms.txt` and `llms-full.txt` files
5. **Review Analysis**: View the pages analyzed and their importance scores

### API Usage (Local Development)

For local development, the backend provides a REST API:

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "max_pages": 20,
    "depth_limit": 3
  }'
```

### API Usage (Production)

In production, the API is available as Vercel functions:

```bash
curl -X POST "https://your-app.vercel.app/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "max_pages": 20,
    "depth_limit": 3
  }'
```

#### Response Format
```json
{
  "llms_txt": "# Site Name\n> Description...",
  "llms_full_txt": "# Site Name - Complete Documentation...",
  "pages_analyzed": [
    {
      "url": "https://example.com/page",
      "title": "Page Title",
      "description": "Page description",
      "content_length": 1500,
      "importance_score": 0.85,
      "section": "Documentation"
    }
  ],
  "generation_time": 3.21
}
```

## 🔧 Configuration

### Crawler Configuration

The crawler can be configured through the API request:

- `max_pages`: Maximum number of pages to crawl (default: 20)
- `depth_limit`: Maximum crawl depth from the root URL (default: 3)

### Content Scoring Algorithm

Pages are scored based on:
- **Keywords in title/URL** (API, docs, tutorial, guide, etc.)
- **URL depth** (closer to root = higher score)
- **Content length** (reasonable length preferred)
- **Link prominence** (pages linked from multiple locations)

### Section Categories

Content is automatically categorized into:
- **API Reference** - API documentation and technical references
- **Getting Started** - Tutorials, guides, quickstart content
- **Documentation** - General documentation pages
- **Examples** - Code examples and demos
- **Support** - FAQ, help, and support pages
- **General** - Other content

## 🚢 Quick Deployment

### Deploy to Vercel (recommended)

**Use the automated deployment script:**
```bash
./deploy-vercel.sh
```

This script automatically:
- Validates all required files (API functions, dependencies, config)
- Builds the Next.js application
- Deploys to Vercel with serverless functions
- Provides deployment URL and testing instructions

### Manual Deployment (alternative)

If you prefer manual deployment to Vercel:

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

### Environment Variables

For production deployment, no environment variables are required as the frontend automatically detects the deployment environment and uses relative API paths.

For custom configurations, you can set:
- `NEXT_PUBLIC_API_URL`: Override the default API URL detection

## 🛠 Deployment Scripts

The project includes two automated scripts to streamline development and deployment:

### 1. Local Development Script (`start.sh`)
```bash
./start.sh
```

**What it does:**
- Creates and activates Python virtual environment
- Installs all backend dependencies from `requirements.txt`
- Starts FastAPI backend server on port 8000
- Starts Next.js development server on port 3000
- Provides clear status messages and error handling

**Perfect for:**
- First-time setup
- Daily development workflow
- Testing changes locally

### 2. Vercel Deployment Script (`deploy-vercel.sh`)
```bash
./deploy-vercel.sh
```

**What it does:**
- Validates all required files exist (API functions, dependencies, config)
- Runs `npm run build` to build the Next.js application
- Executes `vercel --prod` to deploy to production
- Provides deployment URL and testing instructions
- Includes error handling and validation checks

**Perfect for:**
- Production deployments
- CI/CD pipelines
- Ensuring consistent deployments

## �� Project Structure

```
llm-txt-generator/
├── src/                    # Next.js frontend
│   └── app/
│       └── page.tsx       # Main UI component
├── api/                   # Vercel serverless functions
│   ├── generate.py       # Main crawling and generation logic
│   └── health.py         # Health check endpoint
├── backend/              # Local development backend
│   ├── main.py          # FastAPI server (for local dev)
│   ├── requirements.txt # Python dependencies
│   └── venv/           # Virtual environment
├── start.sh             # Local development startup script
├── deploy-vercel.sh     # Vercel deployment script
├── requirements.txt     # Vercel functions dependencies
├── vercel.json         # Vercel configuration
├── package.json        # Frontend dependencies
├── tailwind.config.js  # Tailwind configuration
├── next.config.ts      # Next.js configuration
└── README.md          # This file
```

## 🧪 Testing

### Test Local Backend
```bash
cd backend
source venv/bin/activate
curl http://localhost:8000/health
```

### Test Vercel Functions (after deployment)
```bash
curl https://your-app.vercel.app/api/health
```

### Manual Testing
Try generating llms.txt files for various sites:
- Documentation sites (Next.js, FastAPI docs)
- Company websites
- Open source project pages

## ⚡ Performance Considerations

### Vercel Function Limits
- **Execution Time**: 10 seconds (Hobby), 60 seconds (Pro)
- **Memory**: Up to 1024MB
- **Payload Size**: 4.5MB request/response limit
- **Cold Starts**: ~1-3 seconds for Python functions

### Optimization Tips
- Use smaller `max_pages` values for faster processing
- Consider `depth_limit` to control crawl scope
- Large sites may require Pro plan for longer execution time

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Test locally with `./start.sh`
4. Test deployment with `./deploy-vercel.sh`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Jeremy Howard](https://github.com/jph00) for proposing the llms.txt standard
- [llmstxt.org](https://llmstxt.org/) for the specification
- [Vercel](https://vercel.com/) for serverless function hosting
- The open source community for the amazing tools used in this project

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce
4. Mention whether you're running locally or on Vercel

---

Built with ❤️ for the llms.txt standard 