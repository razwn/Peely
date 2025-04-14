# Peely Chatbot - Serverless Framework Version

This is the Serverless Framework implementation of the Peely chatbot.

## Prerequisites

- Node.js (v20 or later)
- npm
- Python 3.12+
- AWS CLI configured with appropriate credentials
- Serverless Framework (`npm install -g serverless`)


## Environment Variables

Create a `.env` file with the following variables:

```
# AWS Configuration
AWS_REGION=us-east-1
AWS_CHOSEN_REGION=us-east-1

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=peely-index
PINECONE_USE_SERVERLESS=true
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# AWS Bedrock Configuration
BEDROCK_INFERENCE_PROFILE_ARN=arn:aws:bedrock:us-east-1::inference-profile/example-profile
BEDROCK_MISTRAL_MODEL_ID=mistral.mixtral-8x7b-instruct-v0:1
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
CHOSEN_MODEL=claude
```

## Deployment

### Option 1: Using the deployment script

```bash
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual deployment

```bash
# Install dependencies
npm install

# Create lambdas directory structure
mkdir -p lambdas/utils

# Copy files
cp universal_lambda.py lambdas/
cp -r utils/* lambdas/utils/
cp requirements.txt lambdas/

# Deploy with Serverless Framework
npx serverless deploy
```

## Loading the Knowledge Base

After deployment, load your knowledge base:

```bash
python knowledge_loader.py --config utils/content_sources.json
```

## API Usage

After deployment, Serverless Framework will output the API Gateway endpoint URL. You'll also need to retrieve the API key from the AWS Console (API Gateway > API Keys).

### Example Usage

```bash
# Set environment variables for the Streamlit app
export AGW_API_URL="https://your-api-id.execute-api.us-east-1.amazonaws.com/dev"
export AGW_API_KEY="your-api-key-from-aws-console"

# Run the Streamlit app
streamlit run app_streamlit.py
```

## Cleanup

To remove all deployed resources:

```bash
chmod +x teardown.sh
./teardown.sh
```

Or manually:

```bash
npx serverless remove
```