 
FROM python:3.12-slim-bookworm
 
# Install uv

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
 
# Set working directory

WORKDIR /app
 
# Copy dependency files

COPY pyproject.toml ./

COPY uv.lock ./

# Install dependencies using uv

RUN /bin/uv sync --no-install-project
 
# Copy the application into the container.

COPY . /app
 
CMD ["/app/.venv/bin/fastapi", "run", "app_strands_agent/main.py", "--port", "8000"]
 