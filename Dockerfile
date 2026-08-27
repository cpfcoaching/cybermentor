FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create a non-root user for security
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Expose the port Cloud Run expects
EXPOSE 8080

# Start the server
CMD exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080}
