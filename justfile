# Configures your environment for local development
@setup:
  poetry install
  poetry run pre-commit install

# Runs the API
@run:
  poetry run uvicorn src.api.main:app --reload

# Runs all tests
@test:
  poetry run pytest

# Runs the formatter and import sorter
@fmt:
  poetry run black .
  poetry run isort .