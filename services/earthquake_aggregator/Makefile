run-dev:
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source setup_live_config.sh && poetry run python src/main.py

run-dev-historical:
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source setup_historical_config.sh && poetry run python src/main.py

build:
	@echo "Building the docker image for the earthquake_aggregator microservice..."
	docker build -t earthquake_aggregator .

run: build
	@echo "Running the earthquake_aggregator microservice..."
	docker run \
		--network=redpanda_network \
		-e KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		-e KAFKA_TOPIC=earthquakes_aggregated \
		-e KAFKA_CONSUMER_GROUP=earthquakes_aggregated_consumer_group \
		-e WINDOW_DURATION_SECONDS=3600 \
		-e LIVE_OR_HISTORICAL=live \
		earthquake_aggregator
