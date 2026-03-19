#!/usr/bin/env python3
"""
Flow Engineering — Generic Execution Template (Deterministic Layer)

This script performs side effects with validated data.
It only runs AFTER validation passes — never directly after an LLM step.

All actions are logged for telemetry and auditability.

Usage:
  echo '{"decision": "approve", "items": [...]}' | python execute.py
  python execute.py --input validated.json
  python execute.py --input validated.json --dry-run

Output:
  Execution result JSON to stdout.
  Errors to stderr with exit code 1 on failure.

Customize:
  1. Add your action handlers to the ACTIONS dict
  2. Implement each action function
  3. Add telemetry logging to your database
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ── Action Handlers ───────────────────────────────────────────────────

def action_write_file(item: dict, dry_run: bool = False) -> dict:
    """Write result to a file."""
    path = item.get("output_path", "")
    content = item.get("content", "")

    if dry_run:
        return {"id": item.get("id"), "action": "write_file", "status": "dry_run", "path": path}

    # TODO: Implement file write
    # Path(path).write_text(content, encoding="utf-8")

    return {"id": item.get("id"), "action": "write_file", "status": "completed", "path": path}


def action_send_notification(item: dict, dry_run: bool = False) -> dict:
    """Send a notification (Slack, email, webhook, etc.)."""
    channel = item.get("channel", "")
    message = item.get("message", "")

    if dry_run:
        return {"id": item.get("id"), "action": "notify", "status": "dry_run", "channel": channel}

    # TODO: Implement notification
    # Example Slack:
    #   requests.post(SLACK_WEBHOOK, json={"text": message})

    return {"id": item.get("id"), "action": "notify", "status": "completed", "channel": channel}


def action_update_database(item: dict, dry_run: bool = False) -> dict:
    """Update a database record."""
    table = item.get("table", "")
    record_id = item.get("id", "")

    if dry_run:
        return {"id": record_id, "action": "db_update", "status": "dry_run", "table": table}

    # TODO: Implement database update
    # Example:
    #   conn = sqlite3.connect("your.db")
    #   conn.execute("UPDATE ? SET status = ? WHERE id = ?", (table, item["status"], record_id))
    #   conn.commit()

    return {"id": record_id, "action": "db_update", "status": "completed", "table": table}


# Register your action handlers
ACTIONS = {
    "write_file": action_write_file,
    "notify": action_send_notification,
    "db_update": action_update_database,
}


# ── Execution Logic ──────────────────────────────────────────────────

def execute(data: dict, dry_run: bool = False) -> dict:
    """Execute all actions from validated data."""
    start_time = time.time()
    results = []
    errors = []

    items = data.get("items", [])
    for item in items:
        action_type = item.get("action", "")
        handler = ACTIONS.get(action_type)

        if handler is None:
            errors.append({
                "id": item.get("id"),
                "error": f"Unknown action type: {action_type}",
            })
            continue

        try:
            result = handler(item, dry_run=dry_run)
            results.append(result)
        except Exception as e:
            errors.append({
                "id": item.get("id"),
                "action": action_type,
                "error": str(e),
            })

    duration_ms = int((time.time() - start_time) * 1000)
    success = len(errors) == 0

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_ms": duration_ms,
        "dry_run": dry_run,
        "total": len(items),
        "completed": len(results),
        "failed": len(errors),
        "success": success,
        "results": results,
        "errors": errors if errors else None,
    }


def log_telemetry(execution_result: dict, workflow_run_id: str = "") -> None:
    """Log execution to telemetry database."""
    # TODO: Implement telemetry logging
    # See templates/telemetry.sql for the schema
    # Example:
    #   conn = sqlite3.connect("telemetry.db")
    #   conn.execute("""
    #       INSERT INTO step_runs (workflow_run_id, step_name, step_type, duration_ms, success)
    #       VALUES (?, 'execute', 'D', ?, ?)
    #   """, (workflow_run_id, execution_result["duration_ms"], execution_result["success"]))
    #   conn.commit()
    pass


# ── Main ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Execute actions with validated data (D layer)")
    parser.add_argument("--input", help="Read from file instead of stdin")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without executing")
    args = parser.parse_args()

    try:
        # Read input
        if args.input:
            raw = Path(args.input).read_text(encoding="utf-8")
        else:
            raw = sys.stdin.read()

        data = json.loads(raw)
        result = execute(data, dry_run=args.dry_run)

        # Log telemetry
        if not args.dry_run:
            log_telemetry(result)

        print(json.dumps(result, indent=2))

        if not result["success"]:
            sys.exit(1)

    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "step": "execute",
            "success": False,
        }), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
