#!/bin/bash

# Quick Docker Build Script for Kargo Internal

echo "🚀 Building Kargo Internal Docker Image..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t kargo-internal .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "To run the container, use:"
    echo "  docker run -d --name kargo-internal -p 5000:5000 -v \$(pwd)/temp:/app/temp kargo-internal"
    echo ""
    echo "Or use Docker Compose:"
    echo "  docker-compose up -d"
else
    echo "❌ Failed to build Docker image"
    exit 1
fi

