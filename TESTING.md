# Testing Guide for Read Me Later

This project includes a comprehensive test suite covering Python code, shell scripts, Docker configuration, and integration checks.

## Running All Tests

From the project root, run:

```bash
./test.sh
```

This will:
- Create a virtual environment for testing (if needed)
- Install all main and test dependencies
- Run all Python unit tests with coverage reporting
- Lint all shell scripts with ShellCheck
- Validate the Dockerfile for syntax and security best practices
- Build and test the Docker image
- Run integration checks on wrapper scripts and example files

## Output

- **Python Coverage:**  
  Coverage is shown in the terminal and as an HTML report at `tests/htmlcov/index.html`.
- **ShellCheck:**  
  All bash scripts are linted, with clear pass/fail output.
- **Docker:**  
  Dockerfile is validated and a test image is built and checked.
- **Integration:**  
  Checks for the presence and validity of example config files and wrapper scripts.

## Example Output

```text
🐍 Python Unit Tests & Coverage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Running Unit Tests with Coverage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
...
---------- coverage: platform darwin, python 3.9.6-final-0 -----------
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
read_me_later.py                        71      5    93%
--------------------------------------------------------
TOTAL                                   71      5    93%
Coverage HTML written to dir htmlcov

🔍 ShellCheck Linting
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Checking Bash Scripts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ../readlater.sh passed
...
```

## Linting Only

To lint all shell scripts:

```bash
cd tests
./run_tests.sh shellcheck
```

## Adding/Editing Tests

- Python tests: `tests/test_read_me_later.py`
- Shell scripts: Linted automatically
- Test runner: `tests/run_tests.sh`
- Test dependencies: `tests/requirements-test.txt`

## Troubleshooting

- If you see coverage warnings about modules not being imported, ensure the `PYTHONPATH` is set correctly (the test runner does this automatically).
- If Docker or ShellCheck are not installed, those steps will be skipped with a warning.
- For full coverage details, open `tests/htmlcov/index.html` in your browser. 