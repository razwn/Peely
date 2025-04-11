#!/bin/bash
set -e

echo "=== Tearing down Peely Chatbot infrastructure ==="

# Default values
STACK_NAME="PeelyChatbotStack"
FORCE=false
SKIP_CONFIRM=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --stack-name)
      STACK_NAME="$2"
      shift 2
      ;;
    --force)
      FORCE=true
      shift
      ;;
    --yes)
      SKIP_CONFIRM=true
      shift
      ;;
    --help)
      echo "Usage: ./teardown.sh [--stack-name STACK_NAME] [--force] [--yes]"
      echo ""
      echo "Options:"
      echo "  --stack-name STACK_NAME  CloudFormation stack name (default: PeelyChatbotStack)"
      echo "  --force                  Use cdk destroy --force option"
      echo "  --yes                    Skip confirmation prompt"
      echo "  --help                   Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "Error: AWS CDK is not installed. Please install it with: npm install -g aws-cdk"
    exit 1
fi

# Check if stack exists
if ! cdk ls | grep -q "$STACK_NAME"; then
    echo "Error: Stack '$STACK_NAME' not found in CDK app."
    echo "Available stacks:"
    cdk ls
    exit 1
fi

# Ask for confirmation unless --yes is specified
if [ "$SKIP_CONFIRM" = false ]; then
    echo ""
    echo "WARNING: This will delete all resources associated with the Peely Chatbot."
    echo "This includes Lambda functions, API Gateway, DynamoDB tables, and IAM roles."
    echo "Some resources like S3 buckets may need manual cleanup if they contain objects."
    echo ""
    read -p "Are you sure you want to proceed? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Teardown cancelled."
        exit 0
    fi
fi

# Find S3 buckets with data
echo "Checking for S3 buckets to empty..."
BUCKET_PREFIX="peelychatbot"
BUCKETS=$(aws s3api list-buckets --query "Buckets[?starts_with(Name, '$BUCKET_PREFIX')].Name" --output text)

if [ -n "$BUCKETS" ]; then
    echo "The following S3 buckets contain data and may prevent stack deletion:"
    for BUCKET in $BUCKETS; do
        COUNT=$(aws s3 ls s3://$BUCKET --recursive | wc -l)
        if [ $COUNT -gt 0 ]; then
            echo "- $BUCKET ($COUNT objects)"
            
            # Ask to empty bucket
            read -p "Empty this bucket before proceeding? (y/n) " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "Emptying bucket $BUCKET..."
                aws s3 rm s3://$BUCKET --recursive
            else
                echo "Skipping bucket emptying. Note: Stack deletion may fail if buckets are not empty."
            fi
        fi
    done
fi

echo "Starting stack destruction..."

# Run CDK destroy with appropriate options
COMMAND="cdk destroy $STACK_NAME"

if [ "$FORCE" = true ]; then
    COMMAND="$COMMAND --force"
fi

if [ "$SKIP_CONFIRM" = true ]; then
    COMMAND="$COMMAND --require-approval never"
fi

echo "Executing: $COMMAND"
eval $COMMAND

# Verify stack is gone
if aws cloudformation describe-stacks --stack-name $STACK_NAME 2>/dev/null; then
    echo "WARNING: Stack may still exist. Check AWS Console for any resources that need manual cleanup."
else
    echo "Stack successfully deleted."
fi

echo ""
echo "NOTE: You may need to manually delete the following resources if they exist:"
echo "1. CloudWatch Log groups for Lambda functions (typically /aws/lambda/PeelyChatbot*)"
echo "2. ECR repositories with Docker images"
echo "3. Any data in Pinecone or other vector databases"
echo ""
echo "=== Teardown complete ==="