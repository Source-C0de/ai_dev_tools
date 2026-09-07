"""
Loop engineering script — drives the spec → build → test → learn loop.

Usage:
    uv run python scripts/loop.py            # show next 'Doing' task + run tests
    uv run python scripts/loop.py --status   # show backlog status summary
    uv run python scripts/loop.py --complete  # mark the next Doing item as Done
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKLOG = ROOT / "docs" / "backlog.md"
CONTEXT = ROOT / "docs" / "context.md"


def read_backlog() -> str:
    return BACKLOG.read_text()


def find_next_doing(backlog: str) -> tuple[int, str] | None:
    """Return (line_index, line) of the first row whose Status == Doing."""
    rows = iter(enumerate(backlog.splitlines()))
    # skip header + separator
    try:
        for _ in range(2):
            next(rows)
    except StopIteration:
        return None
    for i, line in rows:
        # table row format: `| # | Task | Owner | Loop | Status | Notes |`
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        status = cells[4]
        if status.lower() == "doing":
            return i, line
    return None


def run_tests() -> int:
    print("\n→ Running tests: uv run pytest -q\n")
    result = subprocess.run(
        ["uv", "run", "pytest", "-q"],
        cwd=ROOT,
    )
    return result.returncode


def append_context(backlog: str, doing_line: str, test_passed: bool) -> None:
    task_name = doing_line.split("|")[2].strip() if "|" in doing_line else doing_line
    status = "✅ tests passing" if test_passed else "❌ tests failing"
    entry = (
        f"\n### Loop iteration — task: {task_name}\n"
        f"\nTest result: {status}\n"
    )
    with CONTEXT.open("a") as f:
        f.write(entry)
    print(f"  Appended entry to {CONTEXT.relative_to(ROOT)}")


def mark_line_done(backlog: str, line_index: int) -> str:
    lines = backlog.splitlines()
    line = lines[line_index]
    # Replace the status cell (5th column, index 4) with **Done**.
    parts = line.split("|")
    if len(parts) >= 6:
        parts[5] = " **Done** "
    lines[line_index] = "|".join(parts)
    return "\n".join(lines) + ("\n" if backlog.endswith("\n") else "")


def cmd_status(_args) -> int:
    backlog = read_backlog()
    counts: dict[str, int] = {}
    for line in backlog.splitlines():
        if not line.startswith("|") or line.startswith("| #"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 5:
            counts[cells[4]] = counts.get(cells[4], 0) + 1
    print("Backlog status:")
    for status, n in sorted(counts.items()):
        print(f"  {status}: {n}")
    return 0


def cmd_complete(_args) -> int:
    backlog = read_backlog()
    found = find_next_doing(backlog)
    if not found:
        print("No task currently marked as Doing. Pick one and mark it Doing in backlog.md.")
        return 1
    line_index, line = found
    BACKLOG.write_text(mark_line_done(backlog, line_index))
    print(f"Marked Doing task as Done: {line.split('|')[2].strip()}")
    return 0


def cmd_loop(_args) -> int:
    backlog = read_backlog()
    found = find_next_doing(backlog)
    if not found:
        print("No task currently marked as Doing.")
        print("Edit docs/backlog.md to set one task's Status to 'Doing'.")
        return 0
    _, line = found
    task_name = line.split("|")[2].strip()
    print(f"\nNext 'Doing' task:\n  • {task_name}\n")

    rc = run_tests()
    append_context(backlog, line, test_passed=(rc == 0))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Ties loop engineering driver")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--status", action="store_true", help="Show backlog status")
    group.add_argument("--complete", action="store_true", help="Mark the Doing task as Done")
    args = parser.parse_args()

    if args.status:
        return cmd_status(args)
    if args.complete:
        return cmd_complete(args)
    return cmd_loop(args)


if __name__ == "__main__":
    sys.exit(main())
