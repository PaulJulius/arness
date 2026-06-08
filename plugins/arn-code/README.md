# Arness Code

Structured, artifact-driven development pipeline for Codex and Claude Code. Every feature flows through spec, plan, structure, execute, review, and ship — producing a durable Markdown or JSON artifact at each stage that feeds the next. Three ceremony tiers (swift, standard, thorough) scale process to match scope, from a one-file fix to a cross-cutting refactor. Ships 35 pipeline skills and 17 specialist agents.

## Install

### Codex

```bash
# Add the Arness marketplace (one-time)
codex plugin marketplace add AppsVortex/arness

# Install Arness Code
codex plugin add arn-code@arn-marketplace
```

After installing, start a new Codex thread in your project so the bundled skills load.

### Claude Code

```
# Add the Arness marketplace (one-time)
/plugin marketplace add AppsVortex/arness

# Install this plugin
/plugin install arn-code@arn-marketplace
```

## Use with Codex

Start Codex from the root of the project you want Arness to work on, then prompt with the skill name and the work you want planned:

```
codex "arn-planning add rate limiting to the API"
codex "arn-planning fix #42"
codex "arn-planning pick from backlog"
```

Codex can select installed skills from natural-language prompts when the request matches the skill description. In interactive Codex, you can also type the same skill names directly, for example `arn-planning add rate limiting`.

On first run, `arn-planning` auto-configures the project, creates `.arness/` for specs, plans, task lists, and reports, and writes an `## Arness` configuration block to `CLAUDE.md`. The filename is historical; Arness uses it as its project configuration file even when the workflow is running in Codex.

After planning completes, continue with:

```
arn-implementing   # Execute or resume the plan
arn-shipping       # Commit, push, and open a PR
arn-code-help      # See where you are in the pipeline
```

## Documentation

Full guide: [docs/plugins/arn-code.md](../../docs/plugins/arn-code.md) · [arness.appsvortex.com](https://arness.appsvortex.com/)

## License

MIT. See [LICENSE](./LICENSE).

## Privacy

Arness Code runs inside your host coding agent, such as Codex or Claude Code, on your local machine. The plugin emits no telemetry, collects no usage data, and transmits nothing off-device on its own — all skills and agents operate on files in your working directory. Your host agent handles its own model communication, approval settings, sandboxing, and account-level data controls. Integrations with `git`, the GitHub CLI (`gh`), Bitbucket CLI (`bkt`), and Jira MCP are invoked locally using your existing credentials — the plugin does not intermediate, store, or forward credentials.
