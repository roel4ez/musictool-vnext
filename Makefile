# MusicTool Development Makefile
# Use 'make help' to see available commands

.PHONY: help install dev-install run test lint format type-check clean all-checks

# Default target
help:
	@echo "MusicTool Development Commands"
	@echo "=============================="
	@echo "Setup:"
	@echo "  install      Install dependencies"
	@echo "  dev-install  Install with development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  run          Run the Streamlit application"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         Run ruff linter"
	@echo "  lint-fix     Run ruff linter with auto-fix"
	@echo "  format       Format code with black"
	@echo "  type-check   Run pyright type checking"
	@echo "  all-checks   Run all code quality checks"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        Clean up temporary files"
	@echo "  clean-cache  Clean Python cache files"

# Setup commands
install:
	uv sync

dev-install:
	uv sync --extra dev

# Development commands
run:
	uv run streamlit run app.py

test:
	uv run pytest

test-cov:
	uv run pytest --cov=src/musictool --cov-report=html --cov-report=term

# Code quality commands
lint:
	uv run ruff check src/ tests/ app.py

lint-fix:
	uv run ruff check --fix src/ tests/ app.py

format:
	uv run black src/ tests/ app.py

type-check:
	uv run pyright src/ app.py

# Run all quality checks
all-checks: lint type-check test
	@echo "✅ All checks passed!"

# Cleanup commands
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -f app.log

clean-cache: clean
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pyright_cache" -exec rm -rf {} +
	find . -type d -name "pyrightcache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf .coverage

# Development workflow shortcut
dev: dev-install all-checks
	@echo "🚀 Development environment ready!"
