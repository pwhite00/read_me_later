# Use Python slim image for smaller size
FROM python:3.11-slim

# Set metadata
LABEL maintainer="pwhite00@aol.com"
LABEL description="Read Me Later - A tool for posting messages to Slack via webhooks"
LABEL version="1.0"

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY read_me_later.py .

# Make script executable
RUN chmod +x read_me_later.py

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set entrypoint
ENTRYPOINT ["python", "read_me_later.py"]

# Default command (can be overridden)
CMD ["--help"]