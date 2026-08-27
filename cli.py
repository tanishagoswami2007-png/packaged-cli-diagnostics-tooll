"""Command-line interface."""

from __future__ import annotations

import argparse
import sys

from .config import ConfigError, load_config
from .diagnostics import collect_diagnostics, write_json, write_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="machine-diagnostics",
        description="Inspect a machine and produce a diagnostic report.",
    )
    parser.add_argument("--json", action="store_true", help="Output structured JSON.")
    parser.add_argument("--output", help="Write the report to this file.")
    parser.add_argument("--config", help="Path to a JSON configuration file.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        config = load_config(args.config)
        report = collect_diagnostics(config["developer_tools"])
        if args.json:
            write_json(report, args.output)
        else:
            write_text(report, args.output)
        return 1 if report["summary"]["tools_missing"] else 0
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
