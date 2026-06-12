install:
	uv sync

API_BASE_URL ?= http://localhost:8000
DEV_ADMIN_EMAIL ?= admin@example.local
DEV_PASSWORD ?= devpassword123

BACKUP_DIR ?= backups
BACKUP_FILE ?= $(BACKUP_DIR)/app_db.dump
DB_NAME ?= app_db
DB_SERVICE ?= db
DB_USER ?= app_user
RESTORE_CHECK_DB ?= app_restore_check

run:
	uv run uvicorn app.main:app --reload

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

test:
	docker compose exec api pytest -v

test-coverage:
	docker compose run --rm api pytest \
		--cov=app \
		--cov-report=term-missing \
		--cov-fail-under=85 \
		-v

lint:
	docker compose exec api ruff check .

lint-fix:
	docker compose exec api ruff check . --fix

migration-current:
	docker compose run --rm api alembic current

migration-heads:
	docker compose run --rm api alembic heads

migration-upgrade:
	docker compose run --rm api alembic upgrade head

db-backup:
	bash scripts/db_backup.sh

db-restore-check:
	bash scripts/db_restore_rehearsal.sh

db-backup-dry-run:
	DRY_RUN=true bash scripts/db_backup.sh

db-restore-check-dry-run:
	DRY_RUN=true bash scripts/db_restore_rehearsal.sh

seed:
	docker compose run --rm api python -m app.seed_dev_data

smoke:
	API_BASE_URL=$(API_BASE_URL) DEV_ADMIN_EMAIL=$(DEV_ADMIN_EMAIL) DEV_PASSWORD=$(DEV_PASSWORD) ./scripts/smoke_test.sh

ENVIRONMENT ?= staging
IMAGE_TAG ?= latest

deploy-dry-run:
	ENVIRONMENT=$(ENVIRONMENT) IMAGE_REF=ghcr.io/example/starter-backend-template/api:$(IMAGE_TAG) DRY_RUN=true RUN_MIGRATIONS=true bash scripts/deploy_promote.sh

validate:
	docker compose run --rm api ruff check .
	docker compose run --rm api pytest -v

bootstrap: docker-up migration-upgrade seed smoke

LOAD_REQUESTS ?= 50
LOAD_CONCURRENCY ?= 5
LOAD_API_BASE_URL ?= http://api:8000

load-smoke:
	docker compose run --rm api python perf/load_baseline.py \
		--base-url $(LOAD_API_BASE_URL) \
		--requests $(LOAD_REQUESTS) \
		--concurrency $(LOAD_CONCURRENCY)

load-smoke-ready:
	docker compose run --rm api python perf/load_baseline.py \
		--base-url $(LOAD_API_BASE_URL) \
		--path /health/ready \
		--requests $(LOAD_REQUESTS) \
		--concurrency $(LOAD_CONCURRENCY)
