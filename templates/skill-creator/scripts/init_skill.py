#!/usr/bin/env python3
"""
Flow Engineering — Skill Initializer

Creates a new skill directory with the D-P-D scaffold:
  - SKILL.md (probabilistic layer template)
  - scripts/fetch.py (deterministic: data retrieval)
  - scripts/validate.py (deterministic: output validation)
  - scripts/execute.py (deterministic: side effects)

Usage:
  python init_skill.py my-skill-name
  python init_skill.py my-skill-name --path /custom/skills/dir
"""

import argparse
import os
import sys
import textwrap
from pathlib import Path

DEFAULT_SKILLS_DIR = ".claude/skills"


def create_skill(skill_name: str, base_path: str) -> None:
    """Create a new skill directory with D-P-D scaffold."""
    skill_dir = Path(base_path) / skill_name
    scripts_dir = skill_dir / "scripts"

    if skill_dir.exists():
        print(f"Error: Skill directory already exists: {skill_dir}")
        sys.exit(1)

    scripts_dir.mkdir(parents=True, exist_ok=True)

    # SKILL.md — Probabilistic layer
    skill_md = textwrap.dedent(f"""\
    # Skill: {skill_name}

    ## Description
    {{{{One-line description of what this skill does.}}}}

    ## Trigger
    Use when {{{{describe the trigger condition}}}}.

    ---

    ## Flow (D-P-D Chain)

    ```
    Step 1 [D] -> Fetch input data          (scripts/fetch.py)
    Step 2 [P] -> LLM classifies/generates  (this file)
    Step 3 [D] -> Validate LLM output       (scripts/validate.py)
    Step 4 [D] -> Execute action + log      (scripts/execute.py)
    ```

    ### Step 1: Fetch Input [D]
    Run `scripts/fetch.py` to gather all required input data.

    ### Step 2: LLM Decision [P]
    Given the fetched data, {{{{describe what the LLM should decide}}}}.

    **Required output format (structured JSON):**
    ```json
    {{{{
      "decision": "",
      "confidence": 0.0,
      "reasoning": "",
      "items": []
    }}}}
    ```

    > IMPORTANT: Output MUST be valid JSON. No markdown wrapping.

    ### Step 3: Validate Output [D]
    Run `scripts/validate.py` on the LLM output.

    ### Step 4: Execute [D]
    Run `scripts/execute.py` with the validated output.

    ---

    ## Telemetry
    Log every run to workflow_runs and step_runs tables.

    ## Circuit Breaker
    - Max consecutive failures before break: 3
    - Min confidence to proceed: 0.8
    - Max retry attempts per P step: 2
    """)
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    # scripts/fetch.py — Deterministic: data retrieval
    fetch_py = textwrap.dedent(f"""\
    #!/usr/bin/env python3
    \"\"\"
    {skill_name} — Fetch (Deterministic Layer)

    Retrieves and structures all input data needed for the LLM step.
    This script must be fully deterministic — no LLM calls.

    Returns structured JSON to stdout.
    \"\"\"

    import json
    import sys
    from datetime import datetime, timezone


    def fetch() -> dict:
        \"\"\"Gather input data from all sources.\"\"\"
        # TODO: Replace with actual data retrieval logic
        # Examples:
        #   - Read from database
        #   - Call an API
        #   - Parse a file
        #   - Query a queue

        data = {{
            "items": [],
            "metadata": {{
                "source": "{skill_name}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "count": 0,
            }},
        }}

        return data


    def main():
        try:
            result = fetch()
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(json.dumps({{"error": str(e), "step": "fetch"}}), file=sys.stderr)
            sys.exit(1)


    if __name__ == "__main__":
        main()
    """)
    (scripts_dir / "fetch.py").write_text(fetch_py, encoding="utf-8")

    # scripts/validate.py — Deterministic: output validation
    validate_py = textwrap.dedent(f"""\
    #!/usr/bin/env python3
    \"\"\"
    {skill_name} — Validate (Deterministic Layer)

    Validates LLM output against expected schema and constraints.
    This is the gate between probabilistic and deterministic layers.

    Reads JSON from stdin, validates, outputs validated JSON to stdout.
    Exits with code 1 on validation failure.
    \"\"\"

    import json
    import sys


    # Define your validation schema
    REQUIRED_FIELDS = ["decision", "confidence", "items"]
    VALID_DECISIONS = []  # TODO: Add valid enum values
    CONFIDENCE_MIN = 0.0
    CONFIDENCE_MAX = 1.0


    def validate(data: dict) -> dict:
        \"\"\"Validate LLM output. Raises ValueError on failure.\"\"\"
        errors = []

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {{field}}")

        # Validate decision enum (if VALID_DECISIONS is populated)
        if VALID_DECISIONS and data.get("decision") not in VALID_DECISIONS:
            errors.append(
                f"Invalid decision: {{data.get('decision')}}. "
                f"Must be one of: {{VALID_DECISIONS}}"
            )

        # Validate confidence range
        confidence = data.get("confidence")
        if confidence is not None:
            if not isinstance(confidence, (int, float)):
                errors.append(f"Confidence must be numeric, got: {{type(confidence).__name__}}")
            elif not (CONFIDENCE_MIN <= confidence <= CONFIDENCE_MAX):
                errors.append(
                    f"Confidence {{confidence}} outside range "
                    f"[{{CONFIDENCE_MIN}}, {{CONFIDENCE_MAX}}]"
                )

        # Validate items array
        items = data.get("items")
        if items is not None:
            if not isinstance(items, list):
                errors.append(f"Items must be an array, got: {{type(items).__name__}}")
            elif len(items) == 0:
                errors.append("Items array is empty — at least 1 result required")

        if errors:
            raise ValueError(f"Validation failed: {{'; '.join(errors)}}")

        return data


    def main():
        try:
            raw = sys.stdin.read()
            data = json.loads(raw)
            validated = validate(data)
            print(json.dumps(validated, indent=2))
        except json.JSONDecodeError as e:
            print(json.dumps({{"error": f"Invalid JSON: {{e}}", "step": "validate"}}), file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(json.dumps({{"error": str(e), "step": "validate"}}), file=sys.stderr)
            sys.exit(1)


    if __name__ == "__main__":
        main()
    """)
    (scripts_dir / "validate.py").write_text(validate_py, encoding="utf-8")

    # scripts/execute.py — Deterministic: side effects
    execute_py = textwrap.dedent(f"""\
    #!/usr/bin/env python3
    \"\"\"
    {skill_name} — Execute (Deterministic Layer)

    Performs side effects with validated data.
    This script only runs AFTER validation passes.

    All actions are logged for telemetry and auditability.
    \"\"\"

    import json
    import sys
    import time
    from datetime import datetime, timezone


    def execute(data: dict) -> dict:
        \"\"\"Execute actions with validated data.\"\"\"
        start_time = time.time()
        results = []

        # TODO: Replace with actual execution logic
        # Examples:
        #   - Write to database
        #   - Send notification (Slack, email, webhook)
        #   - Move/create files
        #   - Call external API

        for item in data.get("items", []):
            # Process each item
            results.append({{
                "id": item.get("id"),
                "action": item.get("action"),
                "status": "completed",
            }})

        duration_ms = int((time.time() - start_time) * 1000)

        return {{
            "skill": "{skill_name}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms,
            "results": results,
            "success": True,
        }}


    def main():
        try:
            raw = sys.stdin.read()
            data = json.loads(raw)
            result = execute(data)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(json.dumps({{
                "error": str(e),
                "step": "execute",
                "success": False,
            }}), file=sys.stderr)
            sys.exit(1)


    if __name__ == "__main__":
        main()
    """)
    (scripts_dir / "execute.py").write_text(execute_py, encoding="utf-8")

    print(f"Skill created: {skill_dir}")
    print(f"  SKILL.md          <- P layer (edit prompts and flow here)")
    print(f"  scripts/fetch.py     <- D layer (data retrieval)")
    print(f"  scripts/validate.py  <- D layer (output validation)")
    print(f"  scripts/execute.py   <- D layer (side effects)")


def main():
    parser = argparse.ArgumentParser(
        description="Create a new Flow Engineering skill with D-P-D scaffold"
    )
    parser.add_argument(
        "name",
        help="Skill name (kebab-case, e.g., 'classify-tickets')",
    )
    parser.add_argument(
        "--path",
        default=DEFAULT_SKILLS_DIR,
        help=f"Base directory for skills (default: {DEFAULT_SKILLS_DIR})",
    )
    args = parser.parse_args()

    # Validate name
    if not all(c.isalnum() or c == "-" for c in args.name):
        print("Error: Skill name must be kebab-case (letters, numbers, hyphens only)")
        sys.exit(1)

    create_skill(args.name, args.path)


if __name__ == "__main__":
    main()
