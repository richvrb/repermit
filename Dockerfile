FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV REPERMIT_DATABASE_URL=sqlite:////data/repermit.db

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

RUN useradd --system --uid 10001 repermit && mkdir /data && chown repermit /data
USER repermit
VOLUME /data

EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/ready', timeout=2)"]

CMD ["uvicorn", "repermit.api:app_from_env", "--factory", "--host", "0.0.0.0", "--port", "8000"]
