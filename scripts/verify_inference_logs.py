#!/usr/bin/env python3

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RUNNER = ROOT / "scripts" / "check_proxy_inference.sh"
EXPECTED_TASKS = {"mol-opt-1", "mol-opt-2", "mol-opt-3", "mol-opt-4"}


START_RE = re.compile(r"^\[START\] task=(\S+) env=(\S+) model=(.+)$")
STEP_RE = re.compile(
    r"^\[STEP\] step=(\d+) action=(.+) reward=([0-9]+\.[0-9]{2}) done=(true|false) error=(.+)$"
)
END_RE = re.compile(
    r"^\[END\] success=(true|false) steps=(\d+) score=([0-9]+\.[0-9]{2}) rewards=([0-9]+\.[0-9]{2}(?:,[0-9]+\.[0-9]{2})*)?$"
)


def fail(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not RUNNER.exists():
        fail(f"Missing runner script: {RUNNER}")

    proc = subprocess.run(
        [str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    sys.stderr.write(proc.stderr)

    if proc.returncode != 0:
        sys.stdout.write(proc.stdout)
        fail(f"Runner exited with code {proc.returncode}")

    stdout = proc.stdout
    sys.stdout.write(stdout)

    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        fail("inference.py produced no stdout")

    current_task = None
    seen_tasks = set()
    step_counts = {}
    end_counts = {}

    for line in lines:
        start_match = START_RE.match(line)
        if start_match:
            task_name = start_match.group(1)
            current_task = task_name
            seen_tasks.add(task_name)
            step_counts.setdefault(task_name, 0)
            end_counts.setdefault(task_name, 0)
            continue

        step_match = STEP_RE.match(line)
        if step_match:
            if current_task is None:
                fail(f"Found STEP line before any START: {line}")
            step_counts[current_task] = step_counts.get(current_task, 0) + 1
            continue

        end_match = END_RE.match(line)
        if end_match:
            if current_task is None:
                fail(f"Found END line before any START: {line}")
            end_counts[current_task] = end_counts.get(current_task, 0) + 1
            current_task = None
            continue

        fail(f"Invalid stdout line format: {line}")

    missing_tasks = EXPECTED_TASKS - seen_tasks
    extra_tasks = seen_tasks - EXPECTED_TASKS

    if missing_tasks:
        fail(f"Missing task runs: {sorted(missing_tasks)}")
    if extra_tasks:
        fail(f"Unexpected task runs: {sorted(extra_tasks)}")

    for task in sorted(EXPECTED_TASKS):
        if step_counts.get(task, 0) == 0:
            fail(f"Task {task} produced no STEP lines")
        if end_counts.get(task, 0) != 1:
            fail(f"Task {task} must produce exactly one END line")

    print("[VERIFY] Inference stdout format looks valid for all 4 tasks.", file=sys.stderr)


if __name__ == "__main__":
    main()
