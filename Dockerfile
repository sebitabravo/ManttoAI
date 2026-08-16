FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
# Render CLI crea servicios Docker usando el Dockerfile de la raíz; conservar
# el seed dentro de la imagen mantiene los datos demo idempotentes al arrancar.
COPY scripts/seed_db.py ./seed_db.py

# El artefacto ML no se versiona. Se genera de forma reproducible en el build.
RUN python /app/app/ml/generate_dataset.py && python /app/app/ml/train.py

RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python /app/seed_db.py && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
