FROM public.ecr.aws/lambda/python:3.10

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the dependencies
RUN pip install -r requirements.txt

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}
COPY utils/ ${LAMBDA_TASK_ROOT}/utils/

# Set the CMD to your handler
CMD [ "app.handler" ]