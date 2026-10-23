# ==============================================================================
# STAGE 1: Builder (Alpine)
# Purpose: Compile and install dependencies with minimal footprint
# ==============================================================================
FROM python:3.13-alpine3.20 AS builder

# Install build dependencies required for pip wheel compilation
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    g++ \
    make && \
    rm -rf /var/cache/apk/*

# Create virtual environment in builder stage
WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements-locked.txt .
RUN pip install --no-cache-dir \
    --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    --require-hashes \
    --prefer-binary \
    -r requirements-locked.txt

# ==============================================================================
# STAGE 2: Runtime (Alpine Hardened)
# Purpose: Minimal runtime with security hardening, zero build tools
# ==============================================================================
FROM python:3.13-alpine3.20 AS runtime

# Create non-root user with minimal privileges
RUN addgroup -g 65532 appgroup && \
    adduser -D -u 65532 -G appgroup appuser && \
    mkdir -p /app && \
    chown -R 65532:65532 /app

# Copy virtual environment from builder
COPY --from=builder --chown=65532:65532 /opt/venv /opt/venv

# Set Python environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random

WORKDIR /app

# Copy application files with non-root ownership
COPY --chown=65532:65532 apostille-mirror/analyze_logs.py ./analyze_logs.py
COPY --chown=65532:65532 entrypoint.sh ./entrypoint.sh

# Make entrypoint executable
RUN chmod +x ./entrypoint.sh

# Run as non-root user (UID 65532)
USER 65532:65532

ENTRYPOINT ["python3", "analyze_logs.py"]
