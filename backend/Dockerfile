FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
ARG INSTALL_DEV_REQS=false
RUN pip install --no-cache-dir -r requirements.txt && if [ "${INSTALL_DEV_REQS}" = "true" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

COPY . .

# Render necesita generar el artefacto porque `modelo.joblib` no se versiona.
# Desarrollo/Compose puede omitirlo con `--build-arg SKIP_TRAIN=true`.
ARG SKIP_TRAIN=false
RUN if [ "${SKIP_TRAIN}" != "true" ]; then python /app/app/ml/generate_dataset.py && python /app/app/ml/train.py; fi

RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
