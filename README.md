# Packaged CLI Diagnostics Tool

A small, installable Python command-line tool that inspects a machine and produces:

- Python version information
- Disk-space information
- Environment-variable names (values are redacted)
- Common developer-tool availability
- Structured JSON output
- Human-readable reports
- Useful exit codes
- Unit tests for success, missing dependencies, and malformed configuration paths

## Requirements

- Python 3.9+

## Install

From the project directory:

```bash
python -m pip install .
```

For development/testing:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Usage

Run a human-readable report:

```bash
machine-diagnostics
```

Write JSON:

```bash
machine-diagnostics --json
```

Save JSON to a file:

```bash
machine-diagnostics --json --output report.json
```

Use a configuration file:

```bash
machine-diagnostics --config config/sample_config.json
```

The configuration file contains a list of developer tools to check.

## Exit codes

- `0` = diagnostic completed successfully
- `1` = diagnostic completed but one or more configured developer tools were missing
- `2` = invalid command-line argument or malformed configuration
- `3` = unexpected diagnostic/runtime error

## Example configuration

```json
{
  "developer_tools": ["git", "python", "pip", "node", "npm", "docker"]
}
```

## Security note

Environment-variable **values are never included** in the report. Only variable names are inspected/reported, and values are represented as `<redacted>` when present.

## Project structure

```text
machine_diagnostics/
  __init__.py
  cli.py
  diagnostics.py
  config.py
tests/
  test_diagnostics.py
config/
  sample_config.json
samples/
  sample_report.json
  sample_report.txt
```
