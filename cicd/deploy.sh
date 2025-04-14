#!/bin/bash
set -e

echo "=== Building and deploying Peely Chatbot with Serverless Framework (Container Image) ==="

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "Installing Serverless Framework dependencies..."
  npm install
fi


# Make sure Docker is available
if ! command -v docker &> /dev/null; then
  echo "Docker is not installed or not in PATH. Please install Docker to build the container image."
  exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
  echo "Docker daemon is not running. Please start Docker before continuing."
  exit 1
fi

# Check if user is logged in to AWS ECR
AWS_REGION=${AWS_REGION:-us-east-1}
echo "Checking AWS ECR login status for region: $AWS_REGION"
if ! aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query 'Account' --output text).dkr.ecr.$AWS_REGION.amazonaws.com &> /dev/null; then
  echo "Logging in to AWS ECR..."
  aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query 'Account' --output text).dkr.ecr.$AWS_REGION.amazonaws.com
fi

# Deploy with Serverless Framework
echo "Deploying with Serverless Framework..."
npx serverless deploy

echo "=== Deployment complete ==="
echo ""
echo "Don't forget to load your knowledge base:"
echo "python knowledge_loader.py --config utils/content_sources.json"