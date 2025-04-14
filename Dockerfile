FROM public.ecr.aws/lambda/python:3.11

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the dependencies
RUN pip install -r requirements.txt

# Copy function code and utils
COPY lambdas/universal_lambda.py ${LAMBDA_TASK_ROOT}/universal_lambda.py
COPY utils/ ${LAMBDA_TASK_ROOT}/utils/

# Set the CMD to the handler (could also be done as a parameter override in serverless.yml)
CMD ["universal_lambda.handler"]