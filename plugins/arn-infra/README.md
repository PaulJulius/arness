# Arness Infra

Infrastructure and deployment plugin for Codex and Claude Code. Audits your toolchain, generates Dockerfiles and IaC (OpenTofu, Pulumi, AWS CDK), configures environments and secrets, builds CI/CD pipelines, and walks you through deployment and verification. For complex changes, a structured change management pipeline mirrors the rigor of the development pipeline. Ships 25 infrastructure skills and 10 specialist agents.

> **Experimental — use with care.** Always review generated infrastructure configurations and deployment commands before applying them to real environments. Test in non-production environments first.

## Install

### Codex

```bash
# Add the Arness marketplace (one-time)
codex plugin marketplace add AppsVortex/arness

# Install Arness Infra
codex plugin add arn-infra@arn-marketplace
```

Start Codex in your project and prompt with the Infra wizard:

```bash
codex "arn-infra-wizard"
```

### Claude Code

```
# Add the Arness marketplace (one-time)
/plugin marketplace add AppsVortex/arness

# Install this plugin
/plugin install arn-infra@arn-marketplace
```

### GitHub Copilot

This fork supports GitHub Copilot Chat with repository prompt templates and instructions.
Start the infra workflow by using the same Arness skill name in Copilot Chat, for example:

```text
/arn-infra-wizard
```

Arness preserves `.arness/` artifacts and writes shared project configuration to `CLAUDE.md`.

## Documentation

Full guide: [docs/plugins/arn-infra.md](../../docs/plugins/arn-infra.md) · [arness.appsvortex.com](https://arness.appsvortex.com/)

## License

MIT. See [LICENSE](./LICENSE).

## Privacy

Arness Infra runs inside your host coding agent, such as Codex or Claude Code, on your local machine. The plugin emits no telemetry, collects no usage data, and transmits nothing off-device on its own — all skills and agents operate on files in your working directory. Your host agent handles its own model communication, approval settings, sandboxing, and account-level data controls. Cloud CLIs (`aws`, `gcloud`, `az`, `kubectl`, `tofu`, `pulumi`, `cdk`, `docker`, and similar) and optional MCP integrations are invoked locally using your existing credential configuration — the plugin does not intermediate, store, or forward credentials, and any API calls those tools make go directly from your machine to the respective cloud or service provider.
