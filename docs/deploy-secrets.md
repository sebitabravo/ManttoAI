# Secrets requeridos para deploy (GitHub Actions)

Workflow: `.github/workflows/deploy.yml`

## Secrets obligatorios

- `VPS_HOST`: IP o dominio público del VPS.
- `VPS_USER`: usuario SSH con permisos para desplegar.
- `VPS_SSH_KEY`: clave privada SSH (formato PEM/OpenSSH, sin passphrase para runner).
- `VPS_PROJECT_PATH`: ruta absoluta del proyecto en el VPS (ej. `/home/deploy/manttoai`).
- `SECRET_KEY`: clave JWT segura (`openssl rand -hex 32`).
- `MYSQL_ROOT_PASSWORD`: contraseña MySQL no default.
- `MQTT_PASSWORD`: contraseña MQTT no default.

## Variables de entorno recomendadas para deploy

- `APP_ENV=production`
- `ALLOW_SCHEMA_AUTO_CREATE=false` (default recomendado)
- `ALLOW_RUNTIME_SCHEMA_CHANGES=false` (default recomendado)

> `ALLOW_SCHEMA_AUTO_CREATE` y `ALLOW_RUNTIME_SCHEMA_CHANGES` sólo deben habilitarse temporalmente,
> para escenarios de bootstrap/migración controlados.

## Secret opcional

- `VPS_PORT`: puerto SSH (default `22`).

## Recomendaciones operativas

1. Usar usuario dedicado (evitar `root` directo).
2. Restringir acceso SSH por IP si es posible.
3. Rotar llaves y credenciales al cerrar ciclo académico.
4. Mantener `.env` del VPS fuera de git.
5. Verificar `SECRET_KEY`, credenciales MySQL y MQTT antes de cada deploy.
6. No usar credenciales demo (`manttoai-dev-secret`, `manttoai_root`, `manttoai_mqtt_dev`) fuera de desarrollo.
