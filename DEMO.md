# Demo Guide & Testing

This guide shows how to test and demonstrate the LLMs.txt Generator.

## 🎬 Demo Script

### 1. Start the Application

```bash
# Quick start with the provided script
./start.sh

# Or manually:
# Terminal 1: Backend
cd backend && source venv/bin/activate && python main.py

# Terminal 2: Frontend  
npm run dev
```

### 2. Open the Application
Navigate to `http://localhost:3000` in your browser.

### 3. Demo Walkthrough

#### Step 1: Interface Overview
- Point out the clean, modern UI design
- Highlight the two-column layout
- Show the "About llms.txt" section explaining the standard

#### Step 2: Generate llms.txt for a Documentation Site
Try these test URLs (known to work well):

**Recommended Test Sites:**
- `https://fastapi.tiangolo.com` (FastAPI docs - excellent structure)
- `https://nextjs.org` (Next.js docs - well organized)
- `https://tailwindcss.com` (Tailwind CSS - clear sections)
- `https://vercel.com` (Vercel - good content variety)

**Demo Steps:**
1. Enter URL: `https://fastapi.tiangolo.com`
2. Set max pages to 20 (default)
3. Click "Generate llms.txt"
4. Show the loading state with spinner
5. Point out the real-time feedback

#### Step 3: Review Results
When generation completes:

1. **Success Message**: Show the green success banner with timing
2. **Download Options**: Demonstrate both download buttons
   - `llms.txt` - Curated, organized version
   - `llms-full.txt` - Complete content dump
3. **Pages Analyzed**: Scroll through the analyzed pages showing:
   - Page titles and URLs
   - Section categorization (API Reference, Getting Started, etc.)
   - Importance scores
4. **Preview**: Show the llms.txt preview with proper markdown formatting

#### Step 4: Download and Examine Files
1. Download both files
2. Open in text editor to show structure
3. Point out the organized sections and clear hierarchy

### 4. Technical Demonstration

#### API Testing
```bash
# Test the health endpoint
curl http://localhost:8000/health

# Test the main generation endpoint
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://fastapi.tiangolo.com",
    "max_pages": 10,
    "depth_limit": 2
  }' | jq '.'
```

#### Monitoring System Demo
```bash
# Add a site to monitoring
cd backend && source venv/bin/activate
python monitor.py add "https://fastapi.tiangolo.com" 24

# Check monitoring status
python monitor.py status

# Run a manual check
python monitor.py check "https://fastapi.tiangolo.com"
```

## 🧪 Test Cases

### Test Case 1: Small Documentation Site
- **URL**: `https://tailwindcss.com`
- **Expected**: 15-25 pages, clear categorization
- **Time**: ~10-15 seconds

### Test Case 2: Large API Documentation
- **URL**: `https://docs.github.com`
- **Expected**: Full 50+ pages (if max_pages set high), API references
- **Time**: ~30-60 seconds

### Test Case 3: Simple Company Website
- **URL**: `https://vercel.com`
- **Expected**: 10-20 pages, mixed content types
- **Time**: ~8-12 seconds

### Test Case 4: Error Handling
- **URL**: `https://non-existent-website-12345.com`
- **Expected**: Clear error message
- **Time**: ~5 seconds

### Test Case 5: Rate Limiting Protection
- Make 3-4 rapid requests to test system stability

## 📊 Expected Results

### Good Test Sites (FastAPI example):
```
✅ Generation Complete
Analyzed 18 pages in 12.34 seconds

Sections Generated:
- Getting Started (5 pages)
- Documentation (8 pages) 
- API Reference (3 pages)
- Examples (1 page)
- Support (1 page)
```

### Quality Indicators:
- **High-scoring pages** (0.7-1.0): Documentation, API refs, tutorials
- **Medium-scoring pages** (0.3-0.6): Blog posts, examples
- **Low-scoring pages** (0.0-0.2): Footer pages, legal pages

## 🎯 Key Features to Highlight

### 1. Intelligent Content Discovery
- Show how it finds important pages automatically
- Demonstrate the importance scoring system
- Point out section categorization

### 2. Content Quality Analysis
- Explain how it prioritizes developer-relevant content
- Show filtering of navigation/footer content
- Demonstrate content length optimization

### 3. llms.txt Standard Compliance
- Show the proper markdown structure
- Point out the hierarchical organization
- Demonstrate both summary and detailed versions

### 4. Modern Architecture
- Frontend: Next.js with TypeScript, Tailwind CSS
- Backend: FastAPI with async processing
- Beautiful, responsive design

### 5. Production-Ready Features
- Error handling and validation
- Rate limiting capability
- Monitoring system for automated updates
- Docker deployment support

## 🔍 Troubleshooting Demo Issues

### Common Demo Problems:

1. **Slow Generation**
   - Use smaller sites for quick demos
   - Reduce max_pages to 10-15
   - Pre-warm with a test generation

2. **Network Issues**
   - Have backup test sites ready
   - Test connectivity beforehand
   - Consider localhost examples

3. **Large Sites Timing Out**
   - Set reasonable limits (max_pages: 20)
   - Use well-structured documentation sites
   - Avoid heavy JavaScript sites

### Quick Demo Sites (Fast & Reliable):
- `https://fastapi.tiangolo.com` - 15-20 pages, 10-15 seconds
- `https://tailwindcss.com` - 10-15 pages, 8-10 seconds
- `https://github.com/features` - 20-25 pages, 12-18 seconds

## 📝 Demo Script Template

### 1-Minute Demo:
1. "This is an automated llms.txt generator following the new AI documentation standard"
2. "Enter any website URL..." [enter fastapi.tiangolo.com]
3. "It intelligently crawls and analyzes the site structure" [click generate]
4. "Creates both curated and complete versions" [show downloads]
5. "Perfect for making websites AI-friendly"

### 5-Minute Demo:
1. Explain the llms.txt standard and its importance
2. Show the interface and key features
3. Generate files for a documentation site
4. Review the analysis and categorization
5. Download and examine the generated files
6. Show the monitoring system
7. Discuss deployment options

### 15-Minute Technical Demo:
- Include API testing
- Show monitoring system
- Demonstrate error handling
- Explain the architecture
- Discuss scaling and deployment
- Q&A session

## 🎥 Recording Tips

1. **Screen Setup**: Use 1920x1080 resolution
2. **Browser**: Use Chrome in incognito mode (clean)
3. **Audio**: Test microphone levels beforehand
4. **Preparation**: Have test URLs ready in clipboard
5. **Timing**: Practice the demo flow multiple times
6. **Backup Plan**: Have screenshots ready if live demo fails

---

🎬 **Ready to Demo!** This tool showcases modern web development practices while solving a real problem in the AI documentation space. 