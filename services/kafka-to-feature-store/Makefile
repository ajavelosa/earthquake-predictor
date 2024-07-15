run-dev:
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source ../../setup_credentials.sh && source setup_live_config.sh && poetry run python src/main.py

lint:
	@echo "Linting code..."
	poetry run ruff check --fix

format:
	@echo "Formatting code..."
	poetry run ruff format .

lint-and-format: lint format
