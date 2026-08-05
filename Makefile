.PHONY: setup data train validate run test lint docker-build docker-run

setup:
	python -m pip install -r requirements-dev.txt

data:
	python training/generate_data.py

train: data
	python training/train_model.py

validate:
	python training/validate_model.py

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest -q

lint:
	ruff check .

docker-build:
	docker build -t customer-churn-api:1.0.0 .

docker-run:
	docker run --rm -p 8000:8000 customer-churn-api:1.0.0
