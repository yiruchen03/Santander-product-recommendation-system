#!/bin/bash
# Simple API startup script with logging

cd /Users/chenyiru/Downloads/santander-product-recommendation

echo "========================================="
echo "Starting Santander Recommendation API"
echo "========================================="
echo ""
echo "Checking models directory..."
ls -lh models/*.txt | wc -l
echo ""

echo "Starting uvicorn server..."
echo "URL: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop"
echo ""

uvicorn app:app --host 0.0.0.0 --port 8000 --reload

