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
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	cd backend && ruff check app/ && black --check app/

lint-fix:
	cd backend && ruff check app/ --fix && black app/

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
	docker compose exec backend python /simulator/mqtt_simulator.py --host mosquitto --port 1883 --username "$${MQTT_USERNAME:-manttoai_mqtt}" --password "$${MQTT_PASSWORD:-manttoai_mqtt_dev}" --devices 3 --count 8 --interval 1

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
	mosquitto_pub -h localhost -u "$${MQTT_USERNAME:-manttoai_mqtt}" -P "$${MQTT_PASSWORD:-manttoai_mqtt_dev}" -t "manttoai/equipo/1/lecturas" \
		-m '{"temperatura":45.2,"humedad":60,"vib_x":0.3,"vib_y":0.1,"vib_z":9.8}'
