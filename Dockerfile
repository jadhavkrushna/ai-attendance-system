# Use a stable, official Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for:
# 1. Compiling dlib (cmake, build-essential, libx11-dev, libatlas-base-dev)
# 2. Audio file decoding/processing (libsndfile1)
# 3. Graphics/image loading (libgl1-mesa-glx, libglib2.0-0)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    g++ \
    make \
    libopenblas-dev \
    libsndfile1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency definition file
COPY requirements.txt .

# Limit compiler to a single thread to prevent Out-Of-Memory (OOM) failures on free hosting tiers (Render/Heroku)
ENV MAKEFLAGS="-j1"

# Install dependencies (this compiles dlib which will take a few minutes)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy application code and templates
COPY . .

# Expose Flask web service port
EXPOSE 5000

# Set production environment variables
ENV FLASK_APP=app.py
ENV PORT=5000

# Start Flask with Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
