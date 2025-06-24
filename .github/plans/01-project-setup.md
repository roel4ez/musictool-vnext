# Step 1: Project Setup and Foundation

## Objective
Set up the basic project structure, dependencies, and development environment for the MusicTool MVP.

## Tasks
- [x] Initialize Python project with proper structure
- [x] Create virtual environment and requirements.txt (using uv/pyproject.toml)
- [x] Set up Streamlit application entry point
- [x] Configure basic project metadata (pyproject.toml/setup.py)
- [x] Create basic folder structure for data models, services, and UI
- [x] Set up basic logging configuration
- [x] Create initial README with setup instructions
- [x] Configure ruff for linting with modern settings
- [x] Create Makefile for common development tasks
- [x] Add basic smoke tests for development workflow

## Dependencies to Install
- streamlit
- sqlite3 (built-in)
- pandas
- requests (for Discogs API)
- python-dotenv (for environment variables)
- rapidfuzz (for fuzzy matching)

## Development Tools
- ruff (linting and auto-fixing)
- black (code formatting)
- pyright (type checking)
- pytest (testing framework)
- pytest-cov (coverage reporting)

## Acceptance Criteria
- [x] `uv run streamlit run app.py` launches a basic "Hello World" page
- [x] Virtual environment is properly configured (using uv)
- [x] Project structure follows Python best practices
- [x] All core dependencies are pinned in pyproject.toml
- [x] Ruff linting passes with zero issues
- [x] All development tools work via Makefile commands
- [x] Basic smoke tests pass
