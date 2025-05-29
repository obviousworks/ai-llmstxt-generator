#!/bin/bash

# LLMs.txt Generator - Vercel Deployment Script
echo "🚀 Deploying LLMs.txt Generator to Vercel..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Check if required files exist
echo "🔍 Checking required files..."

required_files=("api/generate.py" "api/health.py" "requirements.txt" "vercel.json")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
done

echo "✅ All required files found"

# Build the frontend
echo "🏗️  Building frontend..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed"
    exit 1
fi

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "🌐 Your app is now live on Vercel"
    echo ""
    echo "📚 Next steps:"
    echo "   1. 🔗 Visit your deployment URL to test the frontend"
    echo "   2. 🧪 Test the API endpoints:"
    echo "      - GET /api/health (health check)"
    echo "      - POST /api/generate (main functionality)"
    echo "   3. 🔒 If you see authentication required:"
    echo "      - This is Vercel's protection feature"
    echo "      - You can disable it in your Vercel dashboard"
    echo "      - Or authenticate through the browser"
    echo "   4. 🌍 For production use:"
    echo "      - Consider setting up a custom domain"
    echo "      - Configure environment variables if needed"
    echo "      - Monitor function performance and costs"
    echo ""
    echo "🎉 Your LLMs.txt Generator is ready to use!"
    echo ""
else
    echo "❌ Deployment failed"
    echo "💡 Common issues:"
    echo "   - Make sure you're logged into Vercel: vercel login"
    echo "   - Check that all required files are present"
    echo "   - Verify your Vercel account has sufficient permissions"
    exit 1
fi 