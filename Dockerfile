# Use official Python 3.10 image (required for Django 5.x)
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.2

# Create and set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (using pip or poetry)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files (with .dockerignore in place)
COPY . .

# Collect static files (if needed)
RUN python manage.py collectstatic --noinput

# Run Daphne ASGI server
CMD ["daphne", "-b", "0.0.0.0", "--port", "$PORT", "chat_project.asgi:application"]