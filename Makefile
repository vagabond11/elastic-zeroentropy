.PHONY: help install install-dev test test-cov lint format clean build publish docs

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=elastic_zeroentropy --cov-report=html --cov-report=term-missing

test-fast: ## Run tests without coverage (faster)
	pytest --no-cov

lint: ## Run linting checks
	flake8 src/ tests/
	mypy src/
	black --check src/ tests/
	isort --check-only src/ tests/

format: ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python -m build

publish: ## Publish to PyPI (requires TWINE_USERNAME and TWINE_PASSWORD)
	twine upload dist/*

publish-test: ## Publish to TestPyPI
	twine upload --repository testpypi dist/*

docs: ## Build documentation
	cd docs && make html

check: ## Run all checks (lint, test, build)
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) build

pre-commit: ## Install pre-commit hooks
	pre-commit install

pre-commit-run: ## Run pre-commit on all files
	pre-commit run --all-files

security: ## Run security checks
	bandit -r src/ -f json -o bandit-report.json
	safety check

update-deps: ## Update dependencies
	pip install --upgrade pip
	pip install --upgrade -e ".[dev]"

version: ## Show current version
	@python -c "import elastic_zeroentropy; print(elastic_zeroentropy.__version__)"

check-version: ## Check if version is consistent
	@echo "Checking version consistency..."
	@python -c "import tomllib; import elastic_zeroentropy; pyproject_version = tomllib.load(open('pyproject.toml', 'rb'))['project']['version']; package_version = elastic_zeroentropy.__version__; assert pyproject_version == package_version, f'Version mismatch: pyproject.toml has {pyproject_version}, package has {package_version}'; print(f'✅ Version consistent: {package_version}')"

bump-version: ## Bump version (usage: make bump-version VERSION=0.1.1)
	@if [ -z "$(VERSION)" ]; then echo "Error: VERSION is required. Usage: make bump-version VERSION=0.1.1"; exit 1; fi
	@python scripts/bump_version.py $(VERSION)

release: ## Prepare for release (usage: make release VERSION=0.1.1)
	@if [ -z "$(VERSION)" ]; then echo "Error: VERSION is required. Usage: make release VERSION=0.1.1"; exit 1; fi
	@echo "🔄 Preparing release for version $(VERSION)..."
	$(MAKE) bump-version VERSION=$(VERSION)
	$(MAKE) check-version
	$(MAKE) build
	@echo "✅ Release prepared for version $(VERSION)"
	@echo "Next steps:"
	@echo "1. git add pyproject.toml src/elastic_zeroentropy/__init__.py"
	@echo "2. git commit -m 'Bump version to $(VERSION)'"
	@echo "3. git tag v$(VERSION)"
	@echo "4. git push origin main"
	@echo "5. git push origin v$(VERSION)"

dev-setup: ## Set up development environment
	$(MAKE) install-dev
	$(MAKE) pre-commit
	$(MAKE) format
	$(MAKE) test 