#!/bin/bash
set -e

echo "=== Building and deploying Peely Chatbot ==="

# Ensure the chatbot_image directory exists
mkdir -p chatbot_image/utils

# Copy files to Docker build directory
echo "Copying files to build directory..."
cp lambda_app.py chatbot_image/app.py  # Rename to avoid confusion with CDK app.py
cp requirements.txt chatbot_image/
cp -r utils/*.py chatbot_image/utils/

# Create Dockerfile directly in the chatbot_image directory
echo "Creating Dockerfile..."
cat > chatbot_image/Dockerfile << 'EOL'
FROM public.ecr.aws/lambda/python:3.12

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the dependencies
RUN pip install -r requirements.txt

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}
COPY utils/ ${LAMBDA_TASK_ROOT}/utils/

# Set the CMD to your handler
CMD [ "app.handler" ]
EOL

# Make sure CDK is bootstrapped
echo "Bootstrapping CDK (if needed)..."
cdk bootstrap

# Synthesize CloudFormation template
echo "Synthesizing CloudFormation template..."
cdk synth

# Deploy with CDK
echo "Deploying infrastructure with CDK..."
cdk deploy --require-approval never

echo "=== Deployment complete ==="
echo "Don't forget to load your knowledge base:"
echo "python knowledge_loader.py --config content_sources.json"