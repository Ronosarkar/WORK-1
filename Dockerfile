# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    IS_CLOUD=1 \
    PORT=7860

# Install system dependencies including FFmpeg and FFprobe
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user (compatible with Hugging Face Spaces & security standards)
RUN useradd -m -u 1000 appuser
WORKDIR /app

# Install Python server dependencies
COPY requirements-server.txt /app/
RUN pip install --no-cache-dir -r requirements-server.txt

# Copy application code
COPY core/ /app/core/
COPY web/ /app/web/
COPY server.py /app/

# Create working directories and assign permissions to non-root user
RUN mkdir -p /app/web_uploads /app/web_exports && \
    chown -R appuser:appuser /app

USER appuser

# Expose port (7860 for Hugging Face Spaces / dynamic $PORT on Render/Koyeb)
EXPOSE 7860

# Launch with Gunicorn production server
CMD ["sh", "-c", "gunicorn -w 1 -k gthread --threads 4 --timeout 300 --bind 0.0.0.0:${PORT:-7860} server:app"]
