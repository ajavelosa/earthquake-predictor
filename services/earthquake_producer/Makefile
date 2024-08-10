run-dev:
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source setup_live_config.sh && poetry run python src/main.py

run-dev-historical:
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source setup_historical_config.sh && poetry run python src/main.py

build:
	@echo "Building the docker image for the earthquake_producer microservice..."
	docker build -t earthquake_producer .

run: build
	@echo "Running the earthquake_producer microservice..."
	docker run \
		--network=redpanda_network \
		-e KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		-e KAFKA_TOPIC=earthquakes \
		-e LIVE_OR_HISTORICAL=live \
		earthquake_producer

lint:
	@echo "Linting code..."
	poetry run ruff check --fix

format:
	@echo "Formatting code..."
	poetry run ruff format .

lint-and-format: lint format
