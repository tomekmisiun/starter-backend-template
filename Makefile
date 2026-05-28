run:
	uvicorn app.main:app --reload

test:
	pytest

install:
	pip install -r requirements.txt