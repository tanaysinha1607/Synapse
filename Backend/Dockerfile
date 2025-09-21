# Use a slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# Copy all backend files into the container
COPY . .
EXPOSE 8000
CMD ["python", "src/main_api.py"]
