FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GARMINTOKENS=/tokens \
    PORT=8000

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code.
COPY garmin_client.py server.py ./
COPY tools ./tools

# Run as a non-root user; the tokens volume is mounted read-only.
RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 8000

CMD ["python", "server.py"]
