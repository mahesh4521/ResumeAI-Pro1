#!/usr/bin/env bash
# Build script for Render deployment
# This script installs both backend and frontend dependencies,
# builds the React frontend, and prepares everything for production.

set -o errexit  # Exit on error

echo "========================================="
echo "  ResumeAI Pro - Production Build Script"
echo "========================================="

# 1. Install Python backend dependencies
echo ""
echo ">>> Installing Python dependencies..."
pip install -r requirements.txt

# 2. Download spacy language model (needed for resume parsing)
echo ""
echo ">>> Downloading spacy language model..."
python -m spacy download en_core_web_sm || echo "Spacy model download skipped (optional)"

# 3. Install Node.js frontend dependencies and build
echo ""
echo ">>> Installing frontend dependencies..."
cd frontend
npm install

echo ""
echo ">>> Building React frontend for production..."
npm run build

cd ..

# 4. Create uploads directory
echo ""
echo ">>> Creating uploads directory..."
mkdir -p uploads/resumes

# 5. Initialize database tables
echo ""
echo ">>> Initializing database..."
python create_all.py || echo "Database initialization skipped (will create on first request)"

echo ""
echo "========================================="
echo "  Build completed successfully!"
echo "========================================="
