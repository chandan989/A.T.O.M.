# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# Multi-stage build:
# Stage 1: Build React frontend
# Stage 2: Build Python environment
# Stage 3: Runtime (serves both API + frontend)

# ── Stage 1: Build the React frontend ──────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /app/atom_web

# Copy frontend source
COPY atom_web/package.json atom_web/package-lock.json* ./
RUN npm ci --ignore-scripts

COPY atom_web/ ./
RUN npm run build

# ── Stage 2: Final runtime ────────────────────────────────
FROM ghcr.io/meta-pytorch/openenv-base:latest

WORKDIR /app/env

# Install curl and build tools if missing
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy the environment code
COPY . /app/env

# Copy the built frontend into a static directory the server can serve
COPY --from=frontend-builder /app/atom_web/dist /app/env/static

# Use pip to install the requirements globally (break-system-packages if debian enforces PEP 668)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --break-system-packages -r server/requirements.txt

# Set PYTHONPATH so imports work correctly
ENV PYTHONPATH="/app/env:$PYTHONPATH"

# Tell the server to serve the frontend static files
ENV SERVE_FRONTEND="true"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Run the FastAPI server
CMD ["sh", "-c", "cd /app/env && uvicorn server.app:app --host 0.0.0.0 --port 7860"]
