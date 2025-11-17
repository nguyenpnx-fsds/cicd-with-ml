FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies (if any)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY train_model.py .

# Create models directory
RUN mkdir -p /app/models

# Run the training pipeline
CMD ["python", "train_model.py"]
