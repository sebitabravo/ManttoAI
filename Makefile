# Makefile — Atajos para ManttoAI
# Uso: make <comando>

.PHONY: up down logs build test lint lint-fix seed backup db-shell simulate train evaluate dev-front lint-front build-front e2e-front mqtt-listen mqtt-test

# === Docker ===
up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose up --build -d

# === Backend ===
test:
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	cd backend && ruff check app/ && black --check app/

lint-fix:
	cd backend && ruff check app/ --fix && black app/

seed:
	python scripts/seed_db.py

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
	cd iot/simulator && python mqtt_simulator.py

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
