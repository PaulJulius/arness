# Arness Implementing

Use this prompt template in GitHub Copilot Chat to continue or resume implementation with Arness.

This repository contains Arness workflows for Claude Code, Codex, and GitHub Copilot. The durable workflow names are the Arness skill names defined in `plugins/arn-code/skills/arn-implementing/SKILL.md` and related files.

- Preserve `.arness/` artifacts and the shared `CLAUDE.md` project configuration block.
- Do not invent a new Copilot plugin API.
- Use the existing Arness workflow name `arn-implementing` when beginning the request.
- If the user’s request is not clear, ask a clarifying question before proceeding.

Example:
`arn-implementing continue the current plan for the payment gateway`