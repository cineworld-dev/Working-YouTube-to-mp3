# Use official Python slim image
FROM python:3.12-slim

# Install ffmpeg & dependencies
RUN apt-get update && apt-get install -y ffmpeg

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port 8080
EXPOSE 8080

# Run the Flask app
CMD ["python", "app.py"]
