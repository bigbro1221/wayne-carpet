# backend/Dockerfile
# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code

COPY .env .
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the backend server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
