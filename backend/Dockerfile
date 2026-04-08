FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
ARG INSTALL_DEV_REQS=false
RUN pip install --no-cache-dir -r requirements.txt && if [ "${INSTALL_DEV_REQS}" = "true" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

COPY . .

# Por defecto se omite entrenamiento en build para mantener builds rápidos/reproducibles.
# Si se requiere artefacto embebido en imagen: --build-arg SKIP_TRAIN=false
ARG SKIP_TRAIN=true
RUN if [ "${SKIP_TRAIN}" != "true" ]; then python /app/app/ml/generate_dataset.py && python /app/app/ml/train.py; fi

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
