# Arness Spark

Greenfield exploration plugin for Codex and Claude Code. Takes a raw idea through product discovery, persona generation, competitive research, brand naming, architecture vision, use case authoring, project scaffolding, visual sketch exploration, and interactive prototype validation — producing a validated concept, a prioritized feature backlog, and a scaffolded codebase ready for development. Ships 28 exploration skills and 20 specialist agents.

## Install

### Codex

```bash
# Add the Arness marketplace (one-time)
codex plugin marketplace add AppsVortex/arness

# Install Arness Spark
codex plugin add arn-spark@arn-marketplace
```

Start Codex in your project and prompt with the Spark entry point:

```bash
codex "arn-brainstorming a scheduling app for home service teams"
```

### Claude Code

```
# Add the Arness marketplace (one-time)
/plugin marketplace add AppsVortex/arness

# Install this plugin
/plugin install arn-spark@arn-marketplace
```

### GitHub Copilot

This fork supports GitHub Copilot Chat with repository prompt templates and instructions.
Start the Spark workflow by using the same Arness skill name in Copilot Chat, for example:

```text
/arn-brainstorming a scheduling app for home service teams
```

Arness preserves `.arness/` artifacts and writes shared project configuration to `CLAUDE.md`.

## Documentation

Full guide: [docs/plugins/arn-spark.md](../../docs/plugins/arn-spark.md) · [arness.appsvortex.com](https://arness.appsvortex.com/)

## License

MIT. See [LICENSE](./LICENSE).

## Privacy

Arness Spark runs inside your host coding agent, such as Codex or Claude Code, on your local machine. The plugin emits no telemetry, collects no usage data, and transmits nothing off-device on its own — all skills and agents operate on files in your working directory. Your host agent handles its own model communication, approval settings, sandboxing, and account-level data controls. Some skills suggest external research — any web browsing, domain lookups, or trademark checks are surfaced as user-driven actions, not plugin-initiated network requests.
