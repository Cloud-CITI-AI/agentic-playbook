# managed-by: agentic-playbook v1.0.0 — required target names (docs/06 §2)
.PHONY: install verify lint format typecheck test-unit test-integration test-contract test-mutation migration-lint build

install:            ## Frozen install from uv.lock
	uv sync --frozen

lint:               ## Ruff lint + format check
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
	uv run ruff check --fix .

typecheck:
	uv run mypy src

test-unit:
	uv run pytest -m "not integration" tests/unit

test-integration:   ## Requires Docker
	uv run pytest -m integration tests/integration

test-contract:      ## Fails if the generated OpenAPI differs from the reviewed snapshot (PY-8)
	uv run python -m scripts.export_openapi > /tmp/openapi.json
	diff -u openapi.json /tmp/openapi.json

test-mutation:      ## Mutation testing on domain code (CI runs on changed files only)
	uv run mutmut run
	uv run python scripts/mutation_gate.py --break 60

migration-lint:
	uv run alembic upgrade head --sql > /tmp/migration.sql
	squawk /tmp/migration.sql

build:
	uv build

verify: lint typecheck test-unit test-integration test-contract
