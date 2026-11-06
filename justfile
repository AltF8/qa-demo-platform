
# QA Development Commands

set default-list := true

# Run all tests
test:
    ./.venv/bin/python -m pytest -q

# Run API tests only
api:
    ./.venv/bin/python -m pytest tests/api -q

# Run the last failed tests
failed:
    ./.venv/bin/python -m pytest --lf

# Debug failed tests with PuDB
debug:
    ./.venv/bin/python -m pytest --pudb -x -s

# Linting
lint:
    ruff check .
    ruff format --check .

# Fix lint errors and format code
format:
    ruff check --fix .
    ruff format .

# Type checking
types:
    basedpyright

# Automatically rerun API tests
watch:
    watchexec -e py -- ./.venv/bin/python -m pytest tests/api -q -x

