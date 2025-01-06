We use Typescript with React and Material UI for frontend.

We use Python with strict typing for backend.

When being asked about specific lines, only return the relevant code, not all the code in the file.

When writing tests for Python, always use pytest function-based tests. Fully annotate the test function.

For JSDoc:
    - Do not add empty lines in the docstring.
    - Do not add type hints in the docstring.

Naming conventions:
    - The transaction registry, when asssigned to variables, should be named df_transaction_registry_all.
    - A function that returns a dictionary should be named map and then what it maps from and to.
        For example, async_map_isin_to_pnl_data, which maps an ISIN code to a PnLData object.
    - A function that takes the transaction registry as an argument can use tr for transaction_registry.
