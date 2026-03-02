# Multi-stage Dockerfile for Mealbot Python service
# Builder stage: install dependencies
# Runtime stage: copy app and run uvicorn

# ---- Builder stage ----
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip

# Copy dependency files
COPY pyproject.toml ./

# Install project dependencies
RUN pip install --no-cache-dir --prefix=/install .

# ---- Runtime stage ----
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY src/ ./src/
COPY static/ ./static/

# Set Python path to include src directory
ENV PYTHONPATH=/app/src
ENV PORT=8080

EXPOSE 8080

# Run the FastAPI application with uvicorn
CMD ["uvicorn", "mealbot_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
