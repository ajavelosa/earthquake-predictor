start-redpanda:
	docker compose -f redpanda.yaml up -d

stop-redpanda:
	docker compose -f redpanda.yaml down

build-feature-pipeline:
	docker compose -f feature_pipeline.yaml build

run-feature-pipeline: build-feature-pipeline
	docker compose -f feature_pipeline.yaml up -d

stop-feature-pipeline:
	docker compose -f feature_pipeline.yaml down
