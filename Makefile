# Makefile — Atajos para ManttoAI
# Uso: make <comando>

.PHONY: setup-env up down logs build config test lint lint-fix seed seed-run backup db-shell simulate train evaluate dev-front lint-front build-front e2e-front mqtt-listen mqtt-test

# === Docker ===
setup-env:
	@test -f .env || cp .env.example .env
	@test -f backend/.env || cp backend/.env.example backend/.env

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

# === Frontend ===
dev-front:
	cd frontend && npm run dev

lint-front:
	cd frontend && npm run lint

build-front:
	cd frontend && npm run build

e2e-front:
	cd frontend && npm run test:e2e

# === IoT ===
simulate:
	docker compose exec backend python /simulator/mqtt_simulator.py --host mosquitto --port 1883 --devices 3 --count 8 --interval 1

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

# === MQTT ===
mqtt-listen:
	mosquitto_sub -h localhost -t "manttoai/#" -v

mqtt-test:
	mosquitto_pub -h localhost -t "manttoai/equipo/1/lecturas" \
		-m '{"temperatura":45.2,"humedad":60,"vib_x":0.3,"vib_y":0.1,"vib_z":9.8}'
