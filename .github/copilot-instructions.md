# GitHub Copilot integration for Arness

This repository contains Arness, a structured workflow system for Claude Code, Codex, and GitHub Copilot. This fork adds Copilot support using repo-local prompt templates and instructions. Upstream `AppsVortex/arness` may not include these files.

- Arness durable workflows are defined by skill names, not host-specific command syntax.
- Claude Code invokes these workflows with slash commands such as `/arn-planning`.
- Codex invokes them by prompting the same skill name, for example `arn-planning add rate limiting`.
- GitHub Copilot should use the prompt templates in `.github/prompts/` or the same Arness skill names such as `/arn-planning`, not invent a new Copilot plugin API.
- Preserve `.arness/` artifacts and the shared `CLAUDE.md` project configuration block.
- Do not skip review gates or replace Arness workflow steps with ad hoc output.
- Keep Claude Code, Codex, and Copilot compatibility in sync by using the same durable workflow names where applicable.

If the user asks for a workflow command, use the relevant Arness entry point and preserve the project’s artifact-driven process.