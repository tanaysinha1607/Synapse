# ============================
# DOCKERFILE — googlegenaiproject backend
# ============================

# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose Cloud Run's expected port
ENV PORT=8080
EXPOSE 8080

# Set environment variables (safe defaults, override in Cloud Run)
ENV GCP_REGION=us-central1
ENV USE_CREWAI=0

# Run the FastAPI app (adjust import path if needed)
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8080"]
