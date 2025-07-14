FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    postgresql-client \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome/Chromium environment variables
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/bin/chromedriver

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download required NLP models and install Playwright browsers
RUN python -c "import spacy; spacy.cli.download('en_core_web_sm')"
RUN python -c "import nltk; nltk.download('stopwords', quiet=True); nltk.download('punkt', quiet=True)"
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Create necessary directories
RUN mkdir -p data/products data/exports logs

# Default command
CMD ["python", "main.py"]