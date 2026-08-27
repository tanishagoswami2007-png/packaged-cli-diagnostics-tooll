"""Core machine diagnostic functions."""

from __future__ import annotations

import json
import os
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def check_tool(tool: str) -> Dict[str, object]:
    executable = shutil.which(tool)
    return {
        "name": tool,
        "available": executable is not None,
        "path": executable,
    }


def collect_environment() -> Dict[str, object]:
    names = sorted(os.environ.keys())
    return {
        "count": len(names),
        "variables": [{"name": name, "value": "<redacted>"} for name in names],
    }


def collect_disk() -> Dict[str, object]:
    usage = shutil.disk_usage(Path.cwd())
    return {
        "path": str(Path.cwd()),
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,
        "free_percent": round((usage.free / usage.total) * 100, 2) if usage.total else 0,
    }


def collect_diagnostics(tools: List[str]) -> Dict[str, object]:
    tool_results = [check_tool(tool) for tool in tools]
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "disk": collect_disk(),
        "environment": collect_environment(),
        "developer_tools": tool_results,
        "summary": {
            "tools_checked": len(tool_results),
            "tools_available": sum(bool(x["available"]) for x in tool_results),
            "tools_missing": sum(not bool(x["available"]) for x in tool_results),
        },
    }


def render_text(report: Dict[str, object]) -> str:
    py = report["python"]
    disk = report["disk"]
    platform_info = report["platform"]
    summary = report["summary"]

    lines = [
        "MACHINE DIAGNOSTICS REPORT",
        "=" * 28,
        f"Timestamp (UTC): {report['timestamp_utc']}",
        "",
        "SYSTEM",
        f"  OS: {platform_info['system']} {platform_info['release']}",
        f"  Machine: {platform_info['machine']}",
        "",
        "PYTHON",
        f"  Version: {py['version']}",
        f"  Executable: {py['executable']}",
        "",
        "DISK",
        f"  Path: {disk['path']}",
        f"  Total: {disk['total_bytes']:,} bytes",
        f"  Used: {disk['used_bytes']:,} bytes",
        f"  Free: {disk['free_bytes']:,} bytes ({disk['free_percent']}%)",
        "",
        "ENVIRONMENT",
        f"  Variables inspected: {report['environment']['count']}",
        "  Values: <redacted>",
        "",
        "DEVELOPER TOOLS",
    ]

    for tool in report["developer_tools"]:
        status = "available" if tool["available"] else "missing"
        path = f" — {tool['path']}" if tool["path"] else ""
        lines.append(f"  {tool['name']}: {status}{path}")

    lines.extend([
        "",
        "SUMMARY",
        f"  Checked: {summary['tools_checked']}",
        f"  Available: {summary['tools_available']}",
        f"  Missing: {summary['tools_missing']}",
    ])
    return "\n".join(lines)


def write_json(report: Dict[str, object], output: str | None) -> None:
    payload = json.dumps(report, indent=2)
    if output:
        Path(output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


def write_text(report: Dict[str, object], output: str | None) -> None:
    payload = render_text(report)
    if output:
        Path(output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
