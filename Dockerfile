# Use official slim base for smaller surface
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# System dependencies for newspaper3k
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    sqlite3 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY . /app

# Environment configuration will be read from `.env` via python-decouple
ENV PYTHONUNBUFFERED=1

# Gunicorn for production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8085", "app:app"]
