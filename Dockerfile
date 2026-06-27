# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port (production uses 3090 via startup.sh)
EXPOSE 3090

# Default command (can be overridden by docker-compose)
CMD ["python", "main.py"]
