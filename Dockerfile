# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder — compiles C++ extensions (dlib, webrtcvad) then discards
#          all build tools so the final image stays small.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Install only the tools needed to compile dlib & webrtcvad
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    g++ \
    make \
    libopenblas-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /install

COPY requirements.prod.txt .

# Limit C++ compilation to 1 thread to stay within free-tier RAM limits
ENV MAKEFLAGS="-j1"
ENV CMAKE_BUILD_PARALLEL_LEVEL=1

# 1. Install CPU-only PyTorch FIRST so pip resolver never touches CUDA packages
RUN pip install --no-cache-dir \
    torch==2.5.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# 2. Install all remaining production dependencies (compiles dlib here)
RUN pip install --no-cache-dir gunicorn -r requirements.prod.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Runtime — copy only installed packages, drop all build tools
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Runtime-only system libraries (no cmake/g++ needed here)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas0 \
    libsndfile1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV PORT=5000

WORKDIR /app

# Copy application source code
COPY . .

EXPOSE 5000

# Run with Gunicorn — 2 workers, 120s timeout for heavy ML inference requests
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
