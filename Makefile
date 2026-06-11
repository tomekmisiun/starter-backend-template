install:
	uv sync

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

lint:
	docker compose exec api ruff check .

lint-fix:
	docker compose exec api ruff check . --fix

db-backup:
	mkdir -p $(BACKUP_DIR)
	docker compose exec -T $(DB_SERVICE) pg_dump -U $(DB_USER) -d $(DB_NAME) -Fc > $(BACKUP_FILE)

db-restore-check:
	test -f $(BACKUP_FILE)
	docker compose exec -T $(DB_SERVICE) dropdb -U $(DB_USER) --if-exists $(RESTORE_CHECK_DB)
	docker compose exec -T $(DB_SERVICE) createdb -U $(DB_USER) $(RESTORE_CHECK_DB)
	docker compose exec -T $(DB_SERVICE) pg_restore -U $(DB_USER) -d $(RESTORE_CHECK_DB) < $(BACKUP_FILE)
	docker compose exec -T $(DB_SERVICE) psql -U $(DB_USER) -d $(RESTORE_CHECK_DB) -c "SELECT 1;"
	docker compose exec -T $(DB_SERVICE) dropdb -U $(DB_USER) --if-exists $(RESTORE_CHECK_DB)
