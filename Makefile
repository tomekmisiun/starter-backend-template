install:
	python -m pip install -r requirements.txt

run:
	python -m uvicorn app.main:app --reload

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