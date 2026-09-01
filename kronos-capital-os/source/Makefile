.PHONY: bootstrap genesis build start stop logs health test lint
bootstrap:
	bash scripts/bootstrap_upstream.sh
genesis:
	python -m kcos.genesis
build:
	docker compose build
start:
	docker compose up -d
stop:
	docker compose down
logs:
	docker compose logs -f --tail=200
health:
	curl -fsS http://127.0.0.1:8080/health | python -m json.tool
test:
	python -m pytest -q
lint:
	python -m compileall -q kcos
