#!/bin/bash

# Exit on error
set -e

# Required environment variables
EC2_HOST=${EC2_HOST:-""}
AWS_REGION=${AWS_REGION:-"us-east-1"}
STAGE_NAME=${STAGE_NAME:-"prod"}
API_NAME="MLOps-Diabetes-API"

# Check required environment variables
if [ -z "$EC2_HOST" ]; then
    echo "Error: EC2_HOST environment variable not set"
    echo "Usage: EC2_HOST=your-ec2-ip ./setup_api_gateway.sh"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed"
    exit 1
fi

echo "Creating API Gateway..."

# Create REST API
API_ID=$(aws apigateway create-rest-api \
    --name "$API_NAME" \
    --description "API Gateway for MLOps Diabetes Prediction" \
    --endpoint-configuration "types=REGIONAL" \
    --query 'id' --output text)

echo "API Gateway created with ID: $API_ID"

# Get root resource ID
ROOT_RESOURCE_ID=$(aws apigateway get-resources \
    --rest-api-id "$API_ID" \
    --query 'items[0].id' \
    --output text)

# Replace placeholder in OpenAPI spec
EC2_ENDPOINT="http://$EC2_HOST:8000"
sed "s|\${EC2_ENDPOINT}|$EC2_ENDPOINT|g" aws/api-gateway.json > aws/api-gateway-deploy.json

# Import API specification
aws apigateway put-rest-api \
    --rest-api-id "$API_ID" \
    --mode overwrite \
    --body "file://aws/api-gateway-deploy.json"

# Create API key
API_KEY=$(aws apigateway create-api-key \
    --name "MLOps-API-Key" \
    --description "API Key for MLOps Diabetes API" \
    --enabled \
    --query 'value' \
    --output text)

# Create usage plan
USAGE_PLAN_ID=$(aws apigateway create-usage-plan \
    --name "MLOps-Usage-Plan" \
    --description "Usage plan for MLOps API" \
    --quota '{"limit": 1000, "period": "MONTH"}' \
    --throttle '{"burstLimit": 10, "rateLimit": 5}' \
    --query 'id' \
    --output text)

# Add API stage to usage plan
aws apigateway create-deployment \
    --rest-api-id "$API_ID" \
    --stage-name "$STAGE_NAME"

aws apigateway update-usage-plan \
    --usage-plan-id "$USAGE_PLAN_ID" \
    --patch-operations \
    op="add",\
    path="/apiStages",\
    value="$API_ID:$STAGE_NAME"

# Add API key to usage plan
aws apigateway create-usage-plan-key \
    --usage-plan-id "$USAGE_PLAN_ID" \
    --key-id "$API_KEY" \
    --key-type "API_KEY"

# Get API Gateway endpoint
API_ENDPOINT="https://$API_ID.execute-api.$AWS_REGION.amazonaws.com/$STAGE_NAME"

echo "API Gateway setup complete!"
echo "API Endpoint: $API_ENDPOINT"
echo "API Key: $API_KEY"

# Save configuration for future reference
cat > api-gateway-config.txt << EOF
API Gateway Configuration
------------------------
API ID: $API_ID
API Endpoint: $API_ENDPOINT
API Key: $API_KEY
Usage Plan ID: $USAGE_PLAN_ID
Stage: $STAGE_NAME
Region: $AWS_REGION
EOF

echo "Configuration saved to api-gateway-config.txt"

# Example curl commands
echo "
Example API calls:
-----------------
# Health check
curl -X GET '$API_ENDPOINT/health' \\
    -H 'x-api-key: $API_KEY'

# Get models
curl -X GET '$API_ENDPOINT/models' \\
    -H 'x-api-key: $API_KEY'

# Make prediction
curl -X POST '$API_ENDPOINT/predict' \\
    -H 'x-api-key: $API_KEY' \\
    -H 'Content-Type: application/json' \\
    -d '{\"features\": [[0,0,0,0,0,0,0,0,0,0]]}'
" 