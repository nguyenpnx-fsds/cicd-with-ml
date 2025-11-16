FROM python:3.11-slim

# Set working directory
WORKDIR /opt/model

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy model code
COPY model.py .

# Set the entrypoint
ENTRYPOINT ["python", "model.py"]
