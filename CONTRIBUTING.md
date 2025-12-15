# Contributing to Game-State

Thank you for your interest in contributing to **Game-State**! Contributions—whether they're bug reports, feature suggestions, code improvements, or documentation—are welcome and appreciated. You will need to use the `uv` project manager to setup this repo and contribute efficiently.

---

## 🛠️ Getting Started

1. Fork the repository and clone your fork.
2. Create a new branch:

   ```
   git checkout -b branch-name
   ```

   Your `branch-name` should prefix one of the following-

   - `feature/<branch-name>`

     - For additional features.

   - `bugfix/<branch-name>`

     - For bug fixes.

   - `enhancement/<branch-name>`

     - For improving or refactoring existing code.

   - `other/<branch-name>`

     - For changes that don’t fit the above categories.

3. Install dependencies:
   ```
   uv sync
   ```

---

## ✅ Guidelines

### Code Style

- Follow [PEP8](https://peps.python.org/pep-0008/).
- Type annotations are required.
- Use docstrings in [Sphinx Style](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html) style.
- Use `basedpyright` for type checking.
- Use `ruff` for linting and formatting.
- If you have `Make` on your system you can run `make` to autoformat and `make check` to type check.

### Commit Messages

- Use clear, descriptive commit messages.
- Prefix with a verb if relevant (e.g., `Fix`, `Add`, `Refactor`, `Document`).
- To make commits, it needs to first pass through `pre-commit`. To set it up run-
  ```
  uv run pre-commit install
  ```

### Tests

- We ues `pytest` wrapped around `coverage.py` for writing, running and analyzing tests.
- If you have `make` on your system-
  - Run `make test` to run the test cases.
  - Run `make coverage` to analyze the test coverage.
- If you don't have `make`-
  - Run `uv run coverage run -m pytest` to run the test cases
  - Run `uv run coverage report` to analyze the test coverage.
- Add tests for any new functionality or bug fixes.
- If additional dependencies are required for tests or the library, add them to `tests/requirements.txt`.

---

## 📚 Documentation

If you're adding new features or modifying the API, please update the relevant docstrings and reStructuredText (`.rst`) documentation in the `docs/` directory.

To build and test docs locally, you can use the `sphinx-autobuild` library:
```
(.venv) $ uv run sphinx-autobuild docs/source docs/_build/html
```

Or via `make`-
```
(.venv) $ make test-docs
```

---

## 🙋 Support & Questions

For questions, open a [discussion](https://github.com/Jiggly-Balls/game-state/discussions) or start a new [issue](https://github.com/Jiggly-Balls/game-state/issues).

---

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same [license](https://github.com/Jiggly-Balls/game-state/blob/main/LICENSE) as the repository.
