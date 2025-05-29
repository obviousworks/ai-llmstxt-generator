# LLMs.txt Generator

An automated tool that generates `llms.txt` files for websites by analyzing their structure and content. This tool follows the [llms.txt specification](https://llmstxt.org/) to create AI-friendly documentation files that help Large Language Models better understand website content.

## 🚀 Features

- **Intelligent Website Crawling**: Automatically discovers and analyzes website pages
- **Content Scoring**: Uses importance algorithms to prioritize key content
- **Section Categorization**: Automatically organizes content into logical sections
- **Dual File Generation**: Creates both `llms.txt` (curated) and `llms-full.txt` (comprehensive)
- **Modern Web Interface**: Beautiful, responsive UI built with Next.js and Tailwind CSS
- **Real-time Progress**: Live feedback during crawling and generation
- **Instant Downloads**: Direct download of generated files

## 🛠 Technology Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Modern styling
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI** - High-performance Python API
- **aiohttp** - Async HTTP client for web crawling
- **BeautifulSoup4** - HTML parsing and content extraction
- **Pydantic** - Data validation and serialization

## 📦 Installation & Setup

### Prerequisites
- **Node.js 18+** (for frontend)
- **Python 3.8+** (for backend)
- **npm or yarn** (package manager)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd llm-txt-generator
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ..  # Back to project root
   npm install
   ```

4. **Start both services**
   
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

5. **Open your browser**
   Navigate to `http://localhost:3000`

## 🎯 Usage

### Web Interface

1. **Enter Website URL**: Input the URL you want to analyze
2. **Configure Settings**: Choose maximum pages to crawl (10-100)
3. **Generate Files**: Click "Generate llms.txt" and wait for processing
4. **Download Results**: Download both `llms.txt` and `llms-full.txt` files
5. **Review Analysis**: View the pages analyzed and their importance scores

### API Usage

The backend provides a REST API for programmatic access:

```bash
curl -X POST "http://localhost:8000/generate" \
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

### Backend Configuration

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

## 🚢 Deployment

### Frontend Deployment (Vercel)

1. **Connect to GitHub**
   ```bash
   npm run build  # Test local build
   ```

2. **Deploy to Vercel**
   - Connect your GitHub repository to Vercel
   - Set build command: `npm run build`
   - Set output directory: `out` (if using static export)

3. **Environment Variables**
   - Set `NEXT_PUBLIC_API_URL` to your backend URL

### Backend Deployment (Railway/Fly.io)

1. **Prepare for deployment**
   ```bash
   cd backend
   echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
   ```

2. **Deploy to Railway**
   - Connect your GitHub repository
   - Railway will auto-detect Python and install dependencies
   - Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Deploy to Fly.io**
   ```bash
   fly auth login
   fly launch
   fly deploy
   ```

### Docker Deployment

1. **Backend Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8000
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Frontend Dockerfile**
   ```dockerfile
   FROM node:18-alpine
   WORKDIR /app
   COPY package*.json ./
   RUN npm install
   COPY . .
   RUN npm run build
   EXPOSE 3000
   CMD ["npm", "start"]
   ```

3. **Docker Compose**
   ```yaml
   version: '3.8'
   services:
     backend:
       build: ./backend
       ports:
         - "8000:8000"
     frontend:
       build: .
       ports:
         - "3000:3000"
       environment:
         - NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

## 📁 Project Structure

```
llm-txt-generator/
├── src/                    # Next.js frontend
│   └── app/
│       └── page.tsx       # Main UI component
├── backend/               # FastAPI backend
│   ├── main.py           # API server and core logic
│   ├── requirements.txt  # Python dependencies
│   └── venv/            # Virtual environment
├── package.json          # Frontend dependencies
├── tailwind.config.js    # Tailwind configuration
├── next.config.js        # Next.js configuration
└── README.md            # This file
```

## 🧪 Testing

### Test the Backend
```bash
cd backend
source venv/bin/activate
python -m pytest tests/  # If you add tests
```

### Test the Frontend
```bash
npm test  # If you add tests
```

### Manual Testing
Try generating llms.txt files for various sites:
- Documentation sites (Next.js, FastAPI docs)
- Company websites
- Open source project pages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Jeremy Howard](https://github.com/jph00) for proposing the llms.txt standard
- [llmstxt.org](https://llmstxt.org/) for the specification
- The open source community for the amazing tools used in this project

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

---

Built with ❤️ for the llms.txt standard
