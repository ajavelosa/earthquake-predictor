# Two step Docker build:
# 1. Build virtual env
# 2. Create the runtime image, used to just run the code provided its virtual environment

# Build virtual env
FROM python:3.10-buster AS builder

# stream output to console
ENV PYTHONUNBUFFERED=1

# install poetry inside the container
RUN pip install poetry==1.8.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# copy the pyproject.toml and poetry.lock files into the container
COPY pyproject.toml poetry.lock /app/

# install Python dependencies from the pyproject.toml file
RUN poetry install

# Create runtime image
FROM python:3.10.3-slim-buster

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# add /app/src to PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

EXPOSE 8501

# copy all the source code into the container
COPY src ./src

CMD ["streamlit", "run", "src/frontend.py", "--server.port=80", "--server.address=0.0.0.0"]
