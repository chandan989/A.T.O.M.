# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# Single-stage build: Python environment + FastAPI server
# (Frontend build removed to speed up Docker builds and avoid npm issues)

FROM ghcr.io/meta-pytorch/openenv-base:latest

WORKDIR /app/env

# Install curl and build tools if missing
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy the environment code (excluding atom_web via .dockerignore)
COPY . /app/env

# Use pip to install the requirements globally (break-system-packages if debian enforces PEP 668)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --break-system-packages -r server/requirements.txt

# Set PYTHONPATH so imports work correctly
ENV PYTHONPATH="/app/env:$PYTHONPATH"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Run the FastAPI server
CMD ["sh", "-c", "cd /app/env && uvicorn server.app:app --host 0.0.0.0 --port 7860"]
