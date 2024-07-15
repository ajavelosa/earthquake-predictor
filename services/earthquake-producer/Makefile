run-dev:
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source setup_live_config.sh && poetry run python src/main.py

build:
	@echo "Building the docker image for the earthquake-producer microservice..."
	docker build -t earthquake-producer .

run: build
	@echo "Running the earthquake-producer microservice..."
	docker run \
		--network=redpanda_network \
		-e KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		-e KAFKA_TOPIC=earthquake \
		-e LIVE_OR_HISTORICAL=live \
		earthquake-producer
