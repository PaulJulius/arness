# Arness Reviewing PR

Use this prompt template in GitHub Copilot Chat to start the `arn-reviewing-pr` workflow.

This repository contains Arness workflows for Claude Code, Codex, and GitHub Copilot. The durable workflow names are the Arness skill names defined in `plugins/arn-code/skills/arn-reviewing-pr/SKILL.md` and related files.

- Preserve `.arness/` artifacts and the shared `CLAUDE.md` project configuration block.
- Do not invent a new Copilot plugin API.
- Use the existing Arness workflow name `arn-reviewing-pr` when beginning the request.
- If the user’s request is not clear, ask a clarifying question before proceeding.

Example:
`arn-reviewing-pr review the branch for the login refactor`