run-dev:
	source ../../setup_credentials.sh && \
	source setup_config.sh && \
	poetry run streamlit run src/frontend.py

build:
	@echo "Building the docker image for the earthquake_dashboard..."
	docker build -t earthquake_dashboard .

run: build
	@echo "Running the earthquake_dashboard microservice..."
	docker run \
		-p 8501:8501 \
		--env-file ../../credentials.env \
		--env-file setup_config.env \
		earthquake_dashboard

lint:
	@echo "Linting code..."
	poetry run ruff check --fix

format:
	@echo "Formatting code..."
	poetry run ruff format .

lint-and-format: lint format
