# Instructions for GitHub Copilot

This repository holds the Pypmanager, a Python 3- and React-based application for displaying
financial portfolio data.

## Co-pilot chat
- When being asked about specific lines, only return the relevant code, not all the code in the file.

## Backend: Python
- Python code must be compatible with Python 3.13
- Use the newest Python language features if possible:
  - Pattern matching
  - Type hints
  - f-strings for string formatting over `%` or `.format()`
  - Dataclasses
  - Walrus operator
- Code quality tools:
  - Formatting: Ruff
  - Linting: PyLint and Ruff
  - Type checking: MyPy
  - Testing: pytest with plain functions and fixtures
- Inline code documentation:
  - File headers should be short and concise:
    ```python
    """Helper for transaction table."""
    ```
  - Every method and function needs a docstring:
    ```python
    async def async_run_function(variable: TypedClass) -> bool:
        """Run async function."""
        ...
    ```
- All code and comments and other text are written in American English
- Follow existing code style patterns as much as possible
- All external I/O operations must be async
- Async patterns:
  - Avoid sleeping in loops
  - Avoid awaiting in loops, gather instead
  - No blocking calls
- Logging:
  - Message format:
    - No periods at end
    - No sensitive data (keys, tokens, passwords), even when those are incorrect.
- Testing:
  - Test location: `tests`
  - Mock external dependencies
  - Follow existing test patterns
- Naming conventions:
  - The transaction registry, when asssigned to variables, should be named df_transaction_registry_all.
  - A function that returns a dictionary should be named map and then what it maps from and to.
    For example, async_map_isin_to_pnl_data, which maps an ISIN code to a PnLData object.
  - A function that takes the transaction registry as an argument can use tr for transaction_registry.

## Frontend: React with typescript
- We use Material UI for rendering standardised components.
- Functions should be documented using the JSDoc format with the following rules:
    - Do not add empty lines in the docstring.
    - Do not add type hints in the docstring.
