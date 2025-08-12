FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_SYSTEM_PYTHON=1 \
    PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# System deps (build tools, ffmpeg for voice, postgres headers for asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates build-essential gcc ffmpeg libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy project files for dependency resolution
COPY pyproject.toml uv.lock ./

# Sync dependencies (prod only)
RUN uv sync --frozen --no-dev

# Copy source
COPY src ./src
COPY scripts ./scripts
COPY main.py ./
COPY README.md ./
COPY questions.example.yaml ./

# Create temp directory for voice files
RUN mkdir -p temp

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]

