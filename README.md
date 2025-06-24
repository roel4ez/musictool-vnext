# MusicTool MVP

A simple desktop application that shows your music collection in one table, displaying which formats you own and providing direct links to Discogs for viewing or purchasing missing tracks.

## Features

- **Digital Collection**: Import from Traktor NML files
- **Physical Collection**: Sync with Discogs via API or import from CSV
- **Unified View**: Single table showing all tracks with format indicators
- **Gap Analysis**: Fuzzy matching to identify missing formats
- **Direct Links**: Quick access to Discogs releases and marketplace

## Quick Start

### Prerequisites

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) (install with `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- A Traktor NML file (optional)
- Discogs account with personal access token (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/roel4ez/musictool-vnext.git
cd musictool-vnext
```

2. Install dependencies and create virtual environment:
```bash
uv sync
# or use the Makefile
make install
```

3. Configure environment (optional):
```bash
cp .env.example .env
# Edit .env with your Discogs token if using API
```

4. Run the application:
```bash
uv run streamlit run app.py
# or use the Makefile
make run
```

The application will open in your browser at `http://localhost:8501`.

## Project Structure

```
musictool-vnext/
├── Makefile               # Development commands and tasks
├── app.py                 # Streamlit application entry point
├── pyproject.toml        # Project configuration and dependencies
├── pyrightconfig.json    # Pyright type checker configuration
├── .env.example          # Environment configuration template
├── src/musictool/        # Main application code
│   ├── models/           # Data models and database schema
│   ├── services/         # Business logic and external integrations
│   └── ui/              # User interface components
├── tests/               # Unit tests
├── data/               # Data files and examples
└── docs/               # Documentation and plans
```

## Development

### Development Setup

Install development dependencies:
```bash
uv sync --extra dev
# or use the Makefile
make dev-install
```

### Common Commands

Use the Makefile for convenient development commands:

```bash
# See all available commands
make help

# Setup and run all checks
make dev

# Run the application
make run

# Run tests
make test

# Run tests with coverage
make test-cov

# Code quality
make lint          # Check code with ruff
make lint-fix      # Fix auto-fixable issues
make format        # Format code with black
make type-check    # Run pyright type checking
make all-checks    # Run all quality checks

# Cleanup
make clean         # Remove temporary files
```

Or use uv directly:

```bash
# Run the application
uv run streamlit run app.py

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/musictool

# Format code
uv run black src/ tests/ app.py

# Lint code
uv run ruff check src/ tests/ app.py

# Type checking
uv run pyright src/ app.py
```

See the implementation plans in `.github/plans/` for detailed development steps.

## License

MIT License - see LICENSE file for details.
