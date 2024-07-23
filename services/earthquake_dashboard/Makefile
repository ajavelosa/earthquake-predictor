run:
	source ../../setup_credentials.sh && \
	source setup_config.sh && \
	poetry run streamlit run src/frontend.py

lint:
	@echo "Linting code..."
	poetry run ruff check --fix

format:
	@echo "Formatting code..."
	poetry run ruff format .

lint-and-format: lint format
