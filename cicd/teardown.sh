#!/bin/bash
set -e

echo "=== Tearing down Peely Chatbot Serverless infrastructure ==="

# Default values
STAGE="dev"
SKIP_CONFIRM=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --stage)
      STAGE="$2"
      shift 2
      ;;
    --yes)
      SKIP_CONFIRM=true
      shift
      ;;
    --help)
      echo "Usage: ./teardown.sh [--stage STAGE] [--yes]"
      echo ""
      echo "Options:"
      echo "  --stage STAGE           Deployment stage (default: dev)"
      echo "  --yes                   Skip confirmation prompt"
      echo "  --help                  Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Check if serverless is installed
if ! command -v npx &> /dev/null; then
    echo "Error: npm/npx is not installed. Please install Node.js and npm."
    exit 1
fi

# Ask for confirmation unless --yes is specified
if [ "$SKIP_CONFIRM" = false ]; then
    echo ""
    echo "WARNING: This will delete all resources associated with the Peely Chatbot."
    echo "This includes Lambda functions, API Gateway, DynamoDB tables, and IAM roles."
    echo ""
    read -p "Are you sure you want to proceed? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Teardown cancelled."
        exit 0
    fi
fi

echo "Running serverless remove for stage: $STAGE"
npx serverless remove --stage $STAGE

echo ""
echo "NOTE: You may need to manually delete any data in Pinecone or other external services."
echo ""
echo "=== Teardown complete ==="