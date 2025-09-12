FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
COPY fixture_service/requirements.txt ./fixture_service_requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r fixture_service_requirements.txt

# Copy application code
COPY . .

# Create directories for generated content
RUN mkdir -p generated_articles match_data topic_data

# Create non-root user and give permissions to app directory
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Debug: Show what files are available
RUN ls -la
RUN ls -la fixture_service/ || echo "fixture_service directory not found"

# Run the fixture service
CMD ["python", "fixture_service/fixture_service.py"]
