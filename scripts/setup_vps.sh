#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin nginx certbot python3-certbot-nginx
sudo systemctl enable --now docker

printf 'VPS preparado. Recordá ajustar DNS, certificados y variables reales antes de producción.\n'
