# AI Concierge Backend

AI-powered car recommendation service using FastAPI. This backend service acts as a chat agent that helps end users get personalized car recommendations using information provided through RAG (Retrieval-Augmented Generation) and MCP (Model Context Protocol) server integrations.

## Prerequisites

- **Python 3.12.6+** - [Download Python](https://www.python.org/downloads/)
- **uv** - Fast Python package manager ([Installation guide](https://github.com/astral-sh/uv))
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Docker** - [Download Docker](https://www.docker.com/get-started)

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-concierge-be
```

### 2. Set Up Environment Variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

#### Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AC_ENV` | Environment mode (`dev` or `prd`) | `dev` | Yes |
| `AC_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` | No |
| `AC_LOG_FORMAT` | Log format (`console` or `json`) | `console` | No |
| **AWS Configuration** |
| `AC_AWS_ACCESS_KEY_ID` | AWS access key for Bedrock/Keyspaces | - | Yes (if using AWS) |
| `AC_AWS_SECRET_ACCESS_KEY` | AWS secret key | - | Yes (if using AWS) |
| `AC_AWS_REGION` | AWS region | - | Yes (if using AWS) |
| `AWS_ACCESS_KEY_ID` | Alternative AWS access key (legacy) | - | No |
| `AWS_SECRET_ACCESS_KEY` | Alternative AWS secret key (legacy) | - | No |
| `AWS_REGION` | Alternative AWS region (legacy) | - | No |
| **AI Model Configuration** |
| `AC_AZURE_AI_ENDPOINT` | Azure OpenAI endpoint URL | - | Yes |
| `AC_AZURE_AI_CREDENTIAL` | Azure OpenAI API key | - | Yes |
| `AC_DEFAULT_MODEL_ID` | Default LLM model ID | `amazon.nova-lite-v1:0` | No |
| `AC_DEFAULT_WORKFLOW_ID` | Default workflow type | `langchain_basic` | No |
| `AC_GEMINI_API_KEY` | Google Gemini API key | - | No |
| **Database Configuration** |
| `AC_CASSANDRA_HOST` | Cassandra/Keyspaces hostname | `127.0.0.1` | Yes |
| `AC_CASSANDRA_PORT` | Cassandra/Keyspaces port | `9042` | Yes |
| `AC_CASSANDRA_KEYSPACE` | Cassandra keyspace name | `ai_concierge` | Yes |
| `AC_CASSANDRA_MODE` | Database mode (`local` or `aws`) | `local` | Yes |
| **Application Configuration** |
| `AC_CONVERSATION_WINDOW_SIZE` | Number of messages to load in context | `20` | No |
| `AC_BASIC_AUTH_PASSWORD` | Basic auth password for API access | - | Yes |
| `AC_HOST` | Server host address | `0.0.0.0` | No |
| `AC_PORT` | Server port | `8000` | No |
| `AC_WORKERS` | Number of worker processes | `4` | No |

> **Note**: All configuration variables are prefixed with `AC_` (AI Concierge). For AWS Cassandra Keyspaces, use `AC_CASSANDRA_MODE=aws` with port `9142`.

### 3. Install Dependencies

Using uv (recommended):

```bash
# Install production dependencies
uv pip install -r pyproject.toml

# Install development dependencies (includes pytest, pre-commit)
uv pip install --group dev
```

### 4. Run Development Server

Start the FastAPI development server:

```bash
# Using uv
uv run fastapi dev

# Or using uvicorn directly
uvicorn app_strands_agent.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 5. Run Tests

Execute the test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_health.py -v
```

## Docker

### Build Docker Image

Build the production-ready Docker image:

```bash
# Build with specific tag
docker build --platform linux/amd64 -t ai-concierge-be:v0.1.0 .
```

### Run Docker Container Locally

```bash
# Run with environment variables
docker run -d \
  --name ai-concierge-be \
  -p 8000:8000 \
  -e AC_ENV=prd \
  -e AC_OPENAI_API_KEY=your_key \
  -e AC_GOOGLE_AI_API_KEY=your_key \
  ai-concierge-be:v0.1.0

# View logs
docker logs -f ai-concierge-be

# Stop container
docker stop ai-concierge-be

# Remove container
docker rm ai-concierge-be
```

### Push to AWS Container Registry (ECR)

#### Step 1: Authenticate Docker to ECR

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 215627216190.dkr.ecr.us-east-1.amazonaws.com
```

#### Step 2: Tag and Push Image

```bash
# Tag the image
docker tag ai-concierge-backend:v0.1.0 215627216190.dkr.ecr.us-east-1.amazonaws.com/ai-concierge-be:v0.1.0

# Push to ECR
docker push 215627216190.dkr.ecr.us-east-1.amazonaws.com/ai-concierge-be:v0.1.0
```
