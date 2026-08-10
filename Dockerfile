# Shared image for the api and watcher services (week 3). Ollama and Chroma
# run as their own official images in docker-compose.yml - this image only
# ever needs to talk to them over the network, never run them in-process.
FROM python:3.11-slim

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --create-home app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ragcore/ ragcore/
COPY api.py ingest_cli.py ask_cli.py watcher_cli.py ./

RUN mkdir -p data/pdfs data/chroma && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
