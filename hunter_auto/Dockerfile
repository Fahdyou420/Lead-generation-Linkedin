FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application files
COPY . .

EXPOSE 5000

# Start Gunicorn server with app and also run the agent schedule
CMD ["python", "main.py"]
