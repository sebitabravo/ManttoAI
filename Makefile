# Makefile — Atajos para ManttoAI
# Uso: make <comando>
#
# Desarrollo local: Docker Compose carga automáticamente docker-compose.yml + docker-compose.override.yml.
# Producción (Dokploy): usar solo docker-compose.yml; ver docs/despliegue-dokploy.md.

.PHONY: setup-env setup-mqtt-creds up down logs build config test lint lint-fix seed seed-run smoke-test backup db-shell simulate verify-3-nodes train evaluate ml-report dev-front lint-front build-front unit-front e2e-front smoke-front mqtt-listen mqtt-test

# === Docker ===
setup-env:
	bash scripts/setup_env.sh

setup-mqtt-creds:
	bash scripts/generate_mosquitto_passwd.sh

up: setup-env config
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose up --build -d

config: setup-env
	docker compose config --quiet

# === Backend ===
test:
	@if [ -x backend/.venv/bin/python ]; then \
		cd backend && .venv/bin/python -m pytest tests/ -v --cov=app --cov-report=term-missing; \
	elif command -v python >/dev/null 2>&1; then \
		cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing; \
	else \
		echo "No se encontró un intérprete Python ejecutable para el runner backend" >&2; \
		exit 127; \
	fi

lint:
	@if [ -x backend/.venv/bin/ruff ] && [ -x backend/.venv/bin/black ]; then \
		cd backend && .venv/bin/ruff check app/ && .venv/bin/black --check app/; \
	elif command -v ruff >/dev/null 2>&1 && command -v black >/dev/null 2>&1; then \
		cd backend && ruff check app/ && black --check app/; \
	else \
		echo "No se encontraron ruff y black ejecutables para el lint backend" >&2; \
		exit 127; \
	fi

lint-fix:
	@if [ -x backend/.venv/bin/ruff ] && [ -x backend/.venv/bin/black ]; then \
		cd backend && .venv/bin/ruff check app/ --fix && .venv/bin/black app/; \
	elif command -v ruff >/dev/null 2>&1 && command -v black >/dev/null 2>&1; then \
		cd backend && ruff check app/ --fix && black app/; \
	else \
		echo "No se encontraron ruff y black ejecutables para el lint backend" >&2; \
		exit 127; \
	fi

seed:
	# Requiere backend en ejecución y montaje de ./scripts en /scripts
	docker compose exec -e APP_ENV=development backend python /scripts/seed_db.py

seed-run:
	docker compose run --rm -e APP_ENV=development backend python /scripts/seed_db.py

smoke-test:
	bash scripts/smoke_test.sh

# === Frontend ===
dev-front:
	cd frontend && npm run dev

lint-front:
	cd frontend && npm run lint

build-front:
	cd frontend && npm run build

unit-front:
	cd frontend && npm run test:unit

e2e-front:
	cd frontend && npm run test:e2e

smoke-front:
	cd frontend && npm run test:unit && npm run test:e2e

# === IoT ===
simulate:
	docker compose exec backend sh -c 'python /simulator/mqtt_simulator.py --host mosquitto --port 1883 --username "$$MQTT_USERNAME" --password "$$MQTT_PASSWORD" --devices 3 --count 8 --interval 1'

verify-3-nodes:
	python scripts/verify_three_nodes.py --api-url "http://localhost:8000" --equipos "1,2,3" --auth-email "$${SEED_ADMIN_EMAIL:-admin@manttoai.local}" --ventana-minutos 10 --max-desfase-segundos 120

# === Base de datos ===
backup:
	./scripts/backup_db.sh

db-shell:
	docker compose exec mysql mysql -u root -p manttoai_db

# === ML ===
train:
	cd backend/app/ml && python generate_dataset.py && python train.py

evaluate:
	cd backend/app/ml && python evaluate.py

ml-report:
	docker compose exec backend python /scripts/generate_ml_report.py

# === MQTT ===
mqtt-listen:
	mosquitto_sub -h localhost -t "manttoai/#" -v

mqtt-test:
	docker compose exec mosquitto sh -c 'mosquitto_pub -h 127.0.0.1 -u "$$MQTT_USERNAME" -P "$$MQTT_PASSWORD" -t "manttoai/telemetria/AA:BB:CC:DD:EE:FF" -m '\''{"temperatura":45.2,"humedad":60,"vib_x":0.3,"vib_y":0.1,"vib_z":9.8}'\'''
