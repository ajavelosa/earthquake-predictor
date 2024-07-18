run-dev:
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source ../../setup_credentials.sh && source setup_live_config.sh && poetry run python src/main.py

run-dev-historical:
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source ../../setup_credentials.sh && source setup_historical_config.sh && poetry run python src/main.py

build:
	@echo "Building the docker image for the seismic_data_sink microservice..."
	docker build -t seismic_data_sink .

run: build
	@echo "Running the seismic_data_sink microservice..."
	docker run \
		--network=redpanda_network \
		-e KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		-e KAFKA_TOPIC=earthquake \
		-e LIVE_OR_HISTORICAL=live \
		--env-file ../../credentials.env \
		--env-file setup_live_config.env \
		seismic_data_sink

lint:
	@echo "Linting code..."
	poetry run ruff check --fix

format:
	@echo "Formatting code..."
	poetry run ruff format .

lint-and-format: lint format
