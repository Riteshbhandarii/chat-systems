# Use official Python 3.10 image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    PIP_NO_CACHE_DIR=1

# Create and set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Collect static files (if needed)
RUN python manage.py collectstatic --noinput

# Create entrypoint script
RUN echo '#!/bin/sh\n\nexec daphne -b 0.0.0.0 --port ${PORT} chat_project.asgi:application' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

# Run Daphne ASGI server
ENTRYPOINT ["/entrypoint.sh"]