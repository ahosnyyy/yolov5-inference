FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

# Install NumPy explicitly first to ensure it's available
RUN pip install --no-cache-dir numpy>=1.18.5

# Then install the rest of the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Clone YOLOv5 repository
RUN git clone https://github.com/ultralytics/yolov5.git

# Create necessary directories
RUN mkdir -p /app/output /app/models

# Copy inference script
COPY inference.py .

# Expose port for FastAPI
EXPOSE 8000

# Set the entrypoint
CMD ["uvicorn", "inference:app", "--host", "0.0.0.0", "--port", "8000"]
