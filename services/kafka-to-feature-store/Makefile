run-dev:
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source ../../setup_credentials.sh && source setup_live_config.sh && poetry run python src/main.py

build:
	@echo "Building the docker image for the kafka-to-feature-store microservice..."
	docker build -t kafka-to-feature-store .

run: build
	@echo "Running the kafka-to-feature-store microservice..."
	docker run \
		--network=redpanda_network \
		-e KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		-e KAFKA_TOPIC=earthquake \
		-e LIVE_OR_HISTORICAL=live \
		--env-file ../../credentials.env \
		--env-file setup_live_config.env \
		kafka-to-feature-store

lint:
	@echo "Linting code..."
	poetry run ruff check --fix

format:
	@echo "Formatting code..."
	poetry run ruff format .

lint-and-format: lint format
