install:
	python -m pip install -r requirements.txt

run:
	python -m uvicorn app.main:app --reload

docker-up:
	docker compose up --build

docker-down:
	docker compose down

test:
	python -m pytest