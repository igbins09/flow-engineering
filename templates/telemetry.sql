-- Flow Engineering — Telemetry Schema
--
-- Three tables for tracking workflow reliability:
--   1. workflow_runs  — One row per complete skill execution
--   2. step_runs      — One row per D or P step within a workflow
--   3. assertions     — One row per validation check within a step
--
-- Usage:
--   sqlite3 telemetry.db < telemetry.sql
--
-- Query examples:
--   -- Success rate by skill (last 7 days)
--   SELECT skill_name,
--          COUNT(*) as total,
--          SUM(CASE WHEN success THEN 1 ELSE 0 END) as succeeded,
--          ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / COUNT(*), 1) as success_pct
--   FROM workflow_runs
--   WHERE started_at > datetime('now', '-7 days')
--   GROUP BY skill_name;
--
--   -- Slowest steps (P90 duration)
--   SELECT step_name, step_type,
--          ROUND(AVG(duration_ms)) as avg_ms,
--          MAX(duration_ms) as max_ms
--   FROM step_runs
--   GROUP BY step_name, step_type
--   ORDER BY avg_ms DESC;
--
--   -- Most common validation failures
--   SELECT assertion_name, COUNT(*) as failures
--   FROM assertions
--   WHERE passed = 0
--   GROUP BY assertion_name
--   ORDER BY failures DESC
--   LIMIT 10;


-- ── Workflow Runs ────────────────────────────────────────────────────
-- Top-level record: one per skill invocation.

CREATE TABLE IF NOT EXISTS workflow_runs (
    id              TEXT PRIMARY KEY,           -- UUID
    skill_name      TEXT NOT NULL,              -- e.g., "classify-tickets"
    started_at      TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at     TEXT,
    duration_ms     INTEGER,
    success         BOOLEAN NOT NULL DEFAULT 0,
    error_message   TEXT,                       -- NULL on success
    input_hash      TEXT,                       -- SHA-256 of input (for regression detection)
    output_hash     TEXT,                       -- SHA-256 of output
    trigger         TEXT,                       -- "manual", "scheduled", "event"
    metadata        TEXT                        -- JSON blob for custom fields
);

CREATE INDEX IF NOT EXISTS idx_workflow_runs_skill ON workflow_runs(skill_name);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_started ON workflow_runs(started_at);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_success ON workflow_runs(success);


-- ── Step Runs ────────────────────────────────────────────────────────
-- One row per step (D or P) within a workflow run.

CREATE TABLE IF NOT EXISTS step_runs (
    id              TEXT PRIMARY KEY,           -- UUID
    workflow_run_id TEXT NOT NULL REFERENCES workflow_runs(id),
    step_name       TEXT NOT NULL,              -- e.g., "fetch", "classify", "validate"
    step_type       TEXT NOT NULL CHECK (step_type IN ('D', 'P')),  -- Deterministic or Probabilistic
    step_order      INTEGER NOT NULL,           -- 1, 2, 3...
    started_at      TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at     TEXT,
    duration_ms     INTEGER,
    success         BOOLEAN NOT NULL DEFAULT 0,
    error_message   TEXT,
    input_hash      TEXT,
    output_hash     TEXT,
    model           TEXT,                       -- LLM model used (P steps only)
    token_count     INTEGER,                    -- Tokens consumed (P steps only)
    cost_usd        REAL,                       -- Cost in USD (P steps only)
    retry_count     INTEGER DEFAULT 0,          -- Number of retries before success/failure
    metadata        TEXT                        -- JSON blob for custom fields
);

CREATE INDEX IF NOT EXISTS idx_step_runs_workflow ON step_runs(workflow_run_id);
CREATE INDEX IF NOT EXISTS idx_step_runs_name ON step_runs(step_name);
CREATE INDEX IF NOT EXISTS idx_step_runs_type ON step_runs(step_type);


-- ── Assertions ───────────────────────────────────────────────────────
-- One row per validation check within a D (validate) step.

CREATE TABLE IF NOT EXISTS assertions (
    id              TEXT PRIMARY KEY,           -- UUID
    step_run_id     TEXT NOT NULL REFERENCES step_runs(id),
    assertion_name  TEXT NOT NULL,              -- e.g., "required_fields", "confidence_range"
    passed          BOOLEAN NOT NULL,
    expected_value  TEXT,                       -- What we expected
    actual_value    TEXT,                       -- What we got
    error_message   TEXT,                       -- NULL if passed
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_assertions_step ON assertions(step_run_id);
CREATE INDEX IF NOT EXISTS idx_assertions_passed ON assertions(passed);
CREATE INDEX IF NOT EXISTS idx_assertions_name ON assertions(assertion_name);
