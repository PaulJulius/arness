# Arness Code Ship

Use this prompt template in GitHub Copilot Chat to start the `arn-code-ship` workflow.

This repository contains Arness workflows for Claude Code, Codex, and GitHub Copilot. The durable workflow names are the Arness skill names defined in `plugins/arn-code/skills/arn-code-ship/SKILL.md` and related files.

- Preserve `.arness/` artifacts and the shared `CLAUDE.md` project configuration block.
- Do not invent a new Copilot plugin API.
- Use the existing Arness workflow name `arn-code-ship` when beginning the request.
- If the user’s request is not clear, ask a clarifying question before proceeding.

Example:
`arn-code-ship prepare this feature for deployment and review`