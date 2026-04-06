#!/usr/bin/env bash
set -euo pipefail

# Instalación mínima en Ubuntu para Docker "bare metal" (sin Dokploy).
# Si usás Dokploy, este script no es necesario: Dokploy gestiona Docker/Traefik.
# Ver docs/despliegue-dokploy.md para despliegue con Dokploy.

sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin nginx certbot python3-certbot-nginx
sudo systemctl enable --now docker

printf 'VPS preparado. Recordá ajustar DNS, certificados y variables reales antes de producción.\n'
printf 'Dokploy: ver docs/despliegue-dokploy.md\n'
