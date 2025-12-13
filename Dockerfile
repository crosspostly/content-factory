FROM ubuntu:22.04
LABEL maintainer="Pavel Shekhov <shekhovpavel@gmail.com>"
LABEL description="Content Factory runtime environment - optimized with --prefer-binary pip caching"
LABEL version="2.1"

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Build arguments for optimization
ARG BUILDKIT_INLINE_CACHE=1
ARG DOCKER_BUILDKIT=1

# Install system dependencies with clean apt cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    ffmpeg \
    imagemagick \
    ghostscript \
    fonts-dejavu-core \
    ca-certificates \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Upgrade pip first (faster layer)
RUN python -m pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /app

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies with --prefer-binary flag
# ⚡ This uses pre-compiled wheels instead of compiling from source
# Expected installation time: 30-40 seconds (vs 60-80 without flag)
RUN pip install --prefer-binary --no-cache-dir -r requirements.txt && \
    echo "✅ Python dependencies installed with --prefer-binary optimization"

# Copy application code
COPY . .

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import core; print('OK')" || exit 1

# Run tests by default
CMD ["python", "-m", "pytest", "-v"]
