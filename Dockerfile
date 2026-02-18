# Use a Debian-based image for easier Tesseract installation
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app
WORKDIR $APP_HOME

# Install Tesseract OCR, Khmer language pack, and other system dependencies
# libgl1-mesa-glx, libsm6, libxext6 are for OpenCV
# poppler-utils is for pdf2image
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-khm \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./app $APP_HOME/app

# Expose the port the app runs on
EXPOSE 8000

# Set the command to run the application
# Using --host 0.0.0.0 makes the app accessible from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
