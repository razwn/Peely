import os
from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway,
    aws_iam as iam,
)
from dotenv import load_dotenv
from constructs import Construct

# Load environment variables from .env file
load_dotenv()


class PeelyChatbotStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB table for conversation history
        conversation_table = dynamodb.Table(
            self, "PeelyConversationHistory",
            partition_key=dynamodb.Attribute(
                name="conversation_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        # Environment variables for Lambda
        environment_variables_dict = {
            "PINECONE_API_KEY": os.environ.get('PINECONE_API_KEY'),
            "PINECONE_INDEX_NAME": os.environ.get('PINECONE_INDEX_NAME'),
            "OPENAI_API_KEY": os.environ.get('OPENAI_API_KEY'),
            "AWS_BEDROCK_REGION": os.environ.get('AWS_BEDROCK_REGION'),
            "BEDROCK_INFERENCE_PROFILE_ARN": os.environ.get('BEDROCK_INFERENCE_PROFILE_ARN'),
            "BEDROCK_MISTRAL_MODEL_ID": os.environ.get('BEDROCK_MISTRAL_MODEL_ID'),
            "CONVERSATION_TABLE_NAME": conversation_table.table_name,
            "CHOSEN_MODEL": os.environ.get('CHOSEN_MODEL'),
        }

        # Create Docker-based Lambda function
        docker_function = _lambda.DockerImageFunction(
            self,
            "PeelyChatbotFunction",
            code=_lambda.DockerImageCode.from_image_asset("./chatbot_image"),
            timeout=Duration.seconds(60),
            memory_size=512,
            architecture=_lambda.Architecture.ARM_64,
            environment=environment_variables_dict
        )

        # Add Bedrock permissions to Lambda role
        docker_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:GetInferenceProfile",
                    "bedrock:ListInferenceProfiles"
                ],
                resources=["*"]
            )
        )

        conversation_table.grant_read_write_data(docker_function)

        api = apigateway.RestApi(
            self, "PeelyChatbotApi",
            rest_api_name="Peely Chatbot API",
            description="API for Peely AI Chatbot",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Api-Key", "Authorization"]
            )
        )

        api_key = apigateway.ApiKey(
            self, "PeelyChatbotApiKey",
            api_key_name="PeelyChatbotApiKey",
            description="API Key for Peely Chatbot",
            enabled=True
        )

        usage_plan = apigateway.UsagePlan(
            self, "PeelyChatbotUsagePlan",
            name="PeelyChatbotUsagePlan",
            description="Usage plan for Peely Chatbot API",
            api_stages=[
                apigateway.UsagePlanPerApiStage(
                    api=api,
                    stage=api.deployment_stage
                )
            ],
            throttle=apigateway.ThrottleSettings(
                rate_limit=10,
                burst_limit=20
            ),
            quota=apigateway.QuotaSettings(
                limit=1000,
                period=apigateway.Period.MONTH
            )
        )

        usage_plan.add_api_key(api_key)

        lambda_integration = apigateway.LambdaIntegration(
            docker_function,
            proxy=True
        )

        conversations = api.root.add_resource("conversations")
        conversations.add_method(
            "GET",
            lambda_integration,
            api_key_required=True
        )
        conversations.add_method(
            "POST",
            lambda_integration,
            api_key_required=True
        )

        conversation = conversations.add_resource("{conversationId}")
        conversation.add_method(
            "GET",
            lambda_integration,
            api_key_required=True
        )

        messages = conversation.add_resource("messages")
        messages.add_method(
            "POST",
            lambda_integration,
            api_key_required=True
        )
        messages.add_method(
            "GET",
            lambda_integration,
            api_key_required=True
        )

        CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="URL of the Peely Chatbot API"
        )
