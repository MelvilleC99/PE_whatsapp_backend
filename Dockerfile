FROM python:3.12-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify OpenAI version at build time
RUN python -c "import openai; print(f'✅ OpenAI version: {openai.__version__}')"

# Copy application
COPY . .

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "300", "--keep-alive", "120", "src.api.webhook_handler:app"]
