# Task-List API Detection

Shared detection rule for skills that depend on host task-list APIs (`TaskList`, `TaskCreate`, `TaskUpdate`, `TaskGet`). Cited by `arn-code-taskify`, `arn-code-execute-plan`, and `arn-code-execute-plan-teams` so they cannot disagree about the same host.

## Capability, not host identity

Task-list availability is a **runtime capability of the host**, not a property of which host you are on. Do NOT infer it from the host name (e.g. "Codex ⇒ no APIs, Claude Code ⇒ has APIs"). A Claude Code session can have Agent Teams enabled while the task-list APIs are absent (they may be granted only to specific subagents and not callable by the lead or a teammate). Detect the capability directly.

Two terms are used throughout the suite:

- **Host task API mode** — the task-list APIs are callable. Use `TaskCreate` / `TaskUpdate` / `TaskList` / `TaskGet`.
- **Codex fallback mode** — the task-list APIs are absent. Drive execution from `TASKS.md` and `PROGRESS_TRACKER.json`; never call the task-list APIs. (Named "Codex fallback" for historical reasons; it applies to **any** host where the probe reports the APIs absent, not just Codex.)

## The probe

Detect with a single **read-only `TaskList` call**. It is idempotent and has no side effects, so it is safe to run as a precondition before any other work.

Never probe with `TaskCreate` or `TaskUpdate` — they mutate state, and on a multi-step skill they typically run *after* expensive setup (e.g. spawning a team), so a failure there forces an unwind instead of a clean route.

Three outcomes:

| Probe result | Interpretation | Mode |
|---|---|---|
| Returns a task list (including an empty list) | APIs callable | Host task API mode |
| Tool is unknown / not callable / `InputValidationError` for an unknown tool | APIs absent | Codex fallback mode |
| Call raises an unexpected error unrelated to tool availability | Treat as absent and fall back; surface the error in the run summary | Codex fallback mode |

## Routing on absence

When the probe reports **APIs absent**, the dependent skill routes to its documented fallback **without prompting** — there is nothing the user can toggle to add the capability, so a blocking prompt is a dead end. Inform the user in one line which fallback is running and why, then proceed.

This is distinct from a **missing Agent Teams env var** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`), which *is* user-fixable: for that case, show setup instructions and suggest the alternative rather than auto-routing.

## Precondition wording for team-based skills

For skills that also require Agent Teams: "Agent Teams enabled" is **necessary but not sufficient**. Both gates must pass, checked in order, before any team is created:

1. **Agent Teams env var set** — else show setup instructions and suggest the subagent-based alternative.
2. **Task-list APIs callable** (this probe) — else auto-route to the subagent-based alternative with a one-line notice.
