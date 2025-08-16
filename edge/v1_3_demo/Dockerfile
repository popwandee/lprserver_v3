# AI Camera v1.3 Demo Dockerfile
# This Dockerfile creates a containerized version of the demo application
# that can run on any platform without hardware dependencies

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEMO_MODE=true
ENV FLASK_ENV=development

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port 5000
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/demo/status || exit 1

# Run the demo application
CMD ["python3", "demo_app.py"]
