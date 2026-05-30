# Contributing to AeroStream

Thank you for your interest in contributing to AeroStream! To maintain code quality, please adhere to the following development practices:

1. **Code Formatting:** All Python code must be formatted using `black` or `pep8` standards.
2. **Testing:** If you alter any mathematical formulas in `src/emissions_calculator.py`, please update and run the test suite using `pytest tests/`.
3. **dbt Changes:** Ensure all new SQL models have corresponding data quality assertions configured inside `dbt_project/models/schema.yml`.
