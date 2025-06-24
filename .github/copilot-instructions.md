# Copilot instructions

## Design Guidelines

When asked to design a feature, or when asked to think about a design, please
follow these guidelines:

- Think about abstractions and best practices in software design.
- Consider scalability, maintainability, and performance.
- Focus on modularity and separation of concerns.
- Use design patterns where appropriate.
- Ensure the design is flexible and can accommodate future changes.
- Challenge assumptions and think critically about the requirements.
- Document any design decisions and rationale behind them, in the form of
Architectural Decision Records (ADRs) in the `docs/adr` directory.

### On diagrams

- Prefer to use mermaid diagrams for visual representations.
- Use clear and concise labels.

## Coding Guidelines

- Write a plan in .github/plans before starting any coding task.
- Work in small, incremental steps.
- Write clean, maintainable code with appropriate comments.
- Provide unit tests for new features and critical code paths.

Use `makefile` for common tasks and commands, such as running tests, linting, and formatting.

### Python

- use `ruff` for linting and style checks.
- use `uv` for dependency management.
- use `pyright` for type checking.

Make sure to run lnting and tests before submitting any code changes.
