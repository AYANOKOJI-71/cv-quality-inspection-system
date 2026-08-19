.PHONY: install test demo web api docker-up fixture

install:
	sudo pip3 install --index-url https://download.pytorch.org/whl/cpu torch==2.5.1+cpu
	sudo pip3 install -e '.[dev]'

test:
	ruff check .
	pytest -q

fixture:
	python scripts/prepare_ksdd_fixture.py --source $(SOURCE) --output data/fixtures

api:
	uvicorn inspection.main:app --app-dir apps/api/src --host 0.0.0.0 --port 4800

web:
	cd apps/web && npx --yes pnpm@10.6.3 dev --host 0.0.0.0 --port 5188

docker-up:
	docker compose up --build
