# Makefile for OpenSpec Python port

.PHONY: install install-dev test lint format clean build publish

# Install package
install:
	pip install -e .

# Install with development dependencies
install-dev:
	pip install -e ".[dev]"

# Run tests
test:
	pytest tests/ -v --cov=openspec --cov-report=html --cov-report=term

# Run linting
lint:
	flake8 src/openspec tests/
	mypy src/openspec

# Format code
format:
	black src/openspec tests/
	isort src/openspec tests/

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	python -m build

# Test the CLI after installation
test-cli:
	openspec --help
	@echo "Testing init command..."
	mkdir -p test_temp_project
	cd test_temp_project && openspec init --non-interactive --ai-tools claude
	cd test_temp_project && openspec view
	cd test_temp_project && openspec change create test-change
	cd test_temp_project && openspec spec create test-spec
	cd test_temp_project && openspec list
	cd test_temp_project && openspec validate
	rm -rf test_temp_project
	@echo "CLI tests passed!"

# Development setup
dev-setup: install-dev
	@echo "Development environment ready!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make test-cli' to test CLI functionality"