#!/usr/bin/env python3
"""Validate Arness repository metadata and documentation inventories.

This script is intentionally dependency-free so contributors and CI can run the
same command from a fresh checkout.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DOC_STEMS = {
    "arn-code": "arn-code",
    "arn-spark": "arn-spark",
    "arn-infra": "arn-infra",
}
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
FRONTMATTER_KEY = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*:\s*")
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.checks = 0

    def check(self, condition: bool, path: Path | str, message: str) -> None:
        self.checks += 1
        if not condition:
            self.errors.append(f"{path}: {message}")

    def load_json(self, path: Path) -> object | None:
        self.check(path.is_file(), path, "expected JSON file to exist")
        if not path.is_file():
            return None

        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.errors.append(f"{path}: invalid JSON at line {exc.lineno}: {exc.msg}")
            return None

    def read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            self.errors.append(f"{path}: expected UTF-8 text: {exc}")
            return ""

    def finish(self) -> int:
        if self.errors:
            print("Arness validation failed:\n")
            for error in self.errors:
                print(f"- {error}")
            print(f"\n{len(self.errors)} error(s) across {self.checks} checks.")
            return 1

        print(f"Arness validation passed ({self.checks} checks).")
        return 0


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def plugin_dirs() -> list[Path]:
    plugins_root = REPO_ROOT / "plugins"
    return sorted(path for path in plugins_root.iterdir() if path.is_dir())


def extract_frontmatter(path: Path, validator: Validator) -> dict[str, str]:
    text = validator.read_text(path)
    lines = text.splitlines()
    validator.check(bool(lines) and lines[0] == "---", path, "missing YAML frontmatter")
    if not lines or lines[0] != "---":
        return {}

    end = None
    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            end = index
            break

    validator.check(end is not None, path, "frontmatter is not closed")
    if end is None:
        return {}

    frontmatter_lines = lines[1:end]
    fields: dict[str, str] = {}
    index = 0
    while index < len(frontmatter_lines):
        line = frontmatter_lines[index]
        if not FRONTMATTER_KEY.match(line):
            index += 1
            continue

        key, raw_value = line.split(":", 1)
        value = raw_value.strip()
        if value in {">", ">-", "|", "|-"}:
            block: list[str] = []
            index += 1
            while index < len(frontmatter_lines):
                next_line = frontmatter_lines[index]
                if FRONTMATTER_KEY.match(next_line):
                    index -= 1
                    break
                block.append(next_line.strip())
                index += 1
            value = " ".join(part for part in block if part)
        elif value == "":
            block = []
            index += 1
            while index < len(frontmatter_lines):
                next_line = frontmatter_lines[index]
                if FRONTMATTER_KEY.match(next_line):
                    index -= 1
                    break
                block.append(next_line.strip())
                index += 1
            value = " ".join(part for part in block if part)

        fields[key] = value.strip("\"'")
        index += 1

    return fields


def skill_files(plugin_dir: Path) -> list[Path]:
    skills_root = plugin_dir / "skills"
    if not skills_root.is_dir():
        return []
    return sorted(skills_root.glob("*/SKILL.md"))


def agent_files(plugin_dir: Path) -> list[Path]:
    agents_root = plugin_dir / "agents"
    if not agents_root.is_dir():
        return []
    return sorted(agents_root.glob("*.md"))


def parse_model_preset(path: Path, validator: Validator) -> dict[str, str]:
    text = validator.read_text(path)
    assignments: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^([a-z0-9-]+):\s*([a-z0-9-]+)\s*$", line)
        if match:
            assignments[match.group(1)] = match.group(2)
    return assignments


def validate_marketplaces(validator: Validator) -> None:
    plugins = {path.name: path for path in plugin_dirs()}

    codex_marketplace_path = REPO_ROOT / ".agents/plugins/marketplace.json"
    codex_marketplace = validator.load_json(codex_marketplace_path)
    if isinstance(codex_marketplace, dict):
        entries = codex_marketplace.get("plugins")
        validator.check(isinstance(entries, list), codex_marketplace_path, "plugins must be a list")
        if isinstance(entries, list):
            names = {entry.get("name") for entry in entries if isinstance(entry, dict)}
            validator.check(names == set(plugins), codex_marketplace_path, "plugin list must match plugins/ directories")
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                source = entry.get("source")
                path_value = source.get("path") if isinstance(source, dict) else None
                validator.check(isinstance(path_value, str), codex_marketplace_path, f"{entry.get('name')} missing source.path")
                if isinstance(path_value, str):
                    target = (REPO_ROOT / path_value).resolve()
                    validator.check(target.is_dir(), codex_marketplace_path, f"{entry.get('name')} source path does not exist: {path_value}")

    claude_marketplace_path = REPO_ROOT / ".claude-plugin/marketplace.json"
    claude_marketplace = validator.load_json(claude_marketplace_path)
    if isinstance(claude_marketplace, dict):
        entries = claude_marketplace.get("plugins")
        validator.check(isinstance(entries, list), claude_marketplace_path, "plugins must be a list")
        if isinstance(entries, list):
            names = {entry.get("name") for entry in entries if isinstance(entry, dict)}
            validator.check(names == set(plugins), claude_marketplace_path, "plugin list must match plugins/ directories")
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                name = entry.get("name")
                source = entry.get("source")
                validator.check(isinstance(source, str), claude_marketplace_path, f"{name} missing source")
                if isinstance(source, str):
                    validator.check((REPO_ROOT / source).is_dir(), claude_marketplace_path, f"{name} source path does not exist: {source}")
                codex_manifest = validator.load_json(REPO_ROOT / f"plugins/{name}/.codex-plugin/plugin.json") if isinstance(name, str) else None
                if isinstance(codex_manifest, dict):
                    validator.check(entry.get("version") == codex_manifest.get("version"), claude_marketplace_path, f"{name} version must match .codex-plugin/plugin.json")

    for name, plugin_dir in plugins.items():
        codex_manifest_path = plugin_dir / ".codex-plugin/plugin.json"
        codex_manifest = validator.load_json(codex_manifest_path)
        if isinstance(codex_manifest, dict):
            validator.check(codex_manifest.get("name") == name, codex_manifest_path, "name must match plugin directory")
            validator.check(isinstance(codex_manifest.get("version"), str) and SEMVER.match(codex_manifest["version"]) is not None, codex_manifest_path, "version must be semver")
            skills_value = codex_manifest.get("skills")
            validator.check(isinstance(skills_value, str), codex_manifest_path, "skills path must be configured")
            if isinstance(skills_value, str):
                validator.check((plugin_dir / skills_value).is_dir(), codex_manifest_path, f"skills path does not exist: {skills_value}")
            interface = codex_manifest.get("interface")
            validator.check(isinstance(interface, dict), codex_manifest_path, "interface must be present")
            if isinstance(interface, dict):
                for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
                    validator.check(bool(interface.get(key)), codex_manifest_path, f"interface.{key} is required")
                validator.check(isinstance(interface.get("defaultPrompt"), list) and bool(interface.get("defaultPrompt")), codex_manifest_path, "interface.defaultPrompt must be a non-empty list")

        claude_manifest_path = plugin_dir / ".claude-plugin/plugin.json"
        claude_manifest = validator.load_json(claude_manifest_path)
        if isinstance(claude_manifest, dict):
            validator.check(claude_manifest.get("name") == name, claude_manifest_path, "name must match plugin directory")
            if "version" in claude_manifest and isinstance(codex_manifest, dict):
                validator.check(claude_manifest.get("version") == codex_manifest.get("version"), claude_manifest_path, "version must match .codex-plugin/plugin.json")


def validate_skills_and_agents(validator: Validator) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    skills_by_plugin: dict[str, set[str]] = {}
    agents_by_plugin: dict[str, set[str]] = {}

    for plugin_dir in plugin_dirs():
        plugin_name = plugin_dir.name
        skills: set[str] = set()
        agents: set[str] = set()

        validator.check(not (plugin_dir / ".claude-plugin/skills").exists(), plugin_dir, "skills must live at plugin root, not inside .claude-plugin")
        validator.check(not (plugin_dir / ".claude-plugin/agents").exists(), plugin_dir, "agents must live at plugin root, not inside .claude-plugin")

        for path in skill_files(plugin_dir):
            fields = extract_frontmatter(path, validator)
            expected_name = path.parent.name
            name = fields.get("name")
            skills.add(name or expected_name)
            validator.check(name == expected_name, path, "frontmatter name must match skill directory")
            validator.check("This skill should be used when" in fields.get("description", ""), path, "description must include skill trigger phrasing")
            validator.check(isinstance(fields.get("version"), str) and SEMVER.match(fields["version"]) is not None, path, "version must be semver")

        for path in agent_files(plugin_dir):
            fields = extract_frontmatter(path, validator)
            expected_name = path.stem
            name = fields.get("name")
            agents.add(name or expected_name)
            validator.check(name == expected_name, path, "frontmatter name must match agent filename")
            validator.check("This agent should be used" in fields.get("description", ""), path, "description must include agent trigger phrasing")
            validator.check(bool(fields.get("tools")), path, "tools field is required")
            validator.check(fields.get("model") in {"opus", "sonnet", "haiku"}, path, "model must be opus, sonnet, or haiku")
            validator.check(bool(fields.get("color")), path, "color field is required")

        preset_dir = plugin_dir / f"skills/{plugin_name}-init/references/agent-models-presets"
        if agents:
            for preset in ("all-opus.md", "balanced.md"):
                preset_path = preset_dir / preset
                validator.check(preset_path.is_file(), preset_path, "agent model preset is required")
                if preset_path.is_file():
                    assignments = parse_model_preset(preset_path, validator)
                    missing = agents - set(assignments)
                    validator.check(not missing, preset_path, f"missing agent assignments: {', '.join(sorted(missing))}")

        skills_by_plugin[plugin_name] = skills
        agents_by_plugin[plugin_name] = agents

    return skills_by_plugin, agents_by_plugin


def validate_reference_docs(
    validator: Validator,
    skills_by_plugin: dict[str, set[str]],
    agents_by_plugin: dict[str, set[str]],
) -> None:
    for plugin_name, doc_stem in PLUGIN_DOC_STEMS.items():
        skills_doc = REPO_ROOT / f"docs/reference/{doc_stem}-skills.md"
        text = validator.read_text(skills_doc)
        listed_skills = table_identifiers(text, "arn-")
        actual_skills = skills_by_plugin.get(plugin_name, set())
        validator.check(listed_skills == actual_skills, skills_doc, missing_extra_message("skills", actual_skills, listed_skills))

        count_match = re.search(r"Complete reference for all (\d+) Arness .*? skills", text)
        validator.check(count_match is not None, skills_doc, "missing skill count sentence")
        if count_match:
            validator.check(int(count_match.group(1)) == len(actual_skills), skills_doc, "skill count must match actual skill directory count")

        agents_doc = REPO_ROOT / f"docs/reference/{doc_stem}-agents.md"
        text = validator.read_text(agents_doc)
        listed_agents = table_identifiers(text, "arn-")
        actual_agents = agents_by_plugin.get(plugin_name, set())
        validator.check(listed_agents == actual_agents, agents_doc, missing_extra_message("agents", actual_agents, listed_agents))

        count_match = re.search(r"Complete reference for all (\d+) Arness .*? agents", text)
        validator.check(count_match is not None, agents_doc, "missing agent count sentence")
        if count_match:
            validator.check(int(count_match.group(1)) == len(actual_agents), agents_doc, "agent count must match actual agent file count")


def missing_extra_message(kind: str, expected: set[str], actual: set[str]) -> str:
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    parts = []
    if missing:
        parts.append(f"missing {kind}: {', '.join(missing)}")
    if extra:
        parts.append(f"unknown {kind}: {', '.join(extra)}")
    return "; ".join(parts) if parts else f"{kind} inventory must match filesystem"


def table_identifiers(text: str, prefix: str) -> set[str]:
    identifiers: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = line.split("|")
        if len(cells) < 3:
            continue
        value = cells[1].strip().strip("`")
        if value.startswith(prefix):
            identifiers.add(value.lstrip("/"))
    return identifiers


def validate_evals(validator: Validator, all_skill_names: set[str]) -> None:
    for path in sorted(REPO_ROOT.glob("plugins/*/skills/*/evals/evals.json")):
        data = validator.load_json(path)
        if not isinstance(data, dict):
            continue
        skill_name = data.get("skill_name")
        validator.check(skill_name in all_skill_names, path, "skill_name must reference an existing skill")
        evals = data.get("evals")
        validator.check(isinstance(evals, list) and bool(evals), path, "evals must be a non-empty list")
        if not isinstance(evals, list):
            continue

        seen_ids: set[object] = set()
        for index, item in enumerate(evals, start=1):
            validator.check(isinstance(item, dict), path, f"eval #{index} must be an object")
            if not isinstance(item, dict):
                continue
            eval_id = item.get("id")
            validator.check(eval_id not in seen_ids, path, f"duplicate eval id: {eval_id}")
            seen_ids.add(eval_id)
            validator.check(bool(item.get("prompt")), path, f"eval {eval_id} missing prompt")
            validator.check(bool(item.get("expected_output")), path, f"eval {eval_id} missing expected_output")
            expectations = item.get("expectations")
            validator.check(isinstance(expectations, list) and bool(expectations), path, f"eval {eval_id} must have non-empty expectations")


def validate_markdown_links(validator: Validator) -> None:
    for path in markdown_files():
        text = validator.read_text(path)
        for target in MARKDOWN_LINK.findall(text):
            if target.startswith(("#", "http://", "https://", "mailto:", "app://")):
                continue
            clean_target = target.strip()
            if is_placeholder_link(clean_target):
                continue
            if clean_target.startswith("<") and clean_target.endswith(">"):
                clean_target = clean_target[1:-1]
            clean_target = clean_target.split()[0].split("#", 1)[0]
            if not clean_target:
                continue
            resolved = (path.parent / unquote(clean_target)).resolve()
            validator.check(resolved.exists(), path, f"local Markdown link target does not exist: {target}")


def markdown_files() -> list[Path]:
    excluded_parts = {".git", ".arness", "node_modules", "dist", "build", "__pycache__", ".aider.chat.history.md"}
    files = []
    for path in REPO_ROOT.rglob("*.md"):
        if excluded_parts.intersection(path.relative_to(REPO_ROOT).parts):
            continue
        files.append(path)
    return sorted(files)


def is_placeholder_link(target: str) -> bool:
    return (
        "[" in target
        or "]" in target
        or " " in target
        or target.startswith("REPO-")
        or re.search(r"(^|/)(F|UC)-\d{3}", target) is not None
    )


def validate_path_hygiene(validator: Validator) -> None:
    user_home_unix = re.compile("/" + "Users" + r"/(?!\.\.\.)[A-Za-z0-9._-]+")
    user_home_linux = re.compile("/" + "home" + r"/(?!(username|user)\b)[A-Za-z0-9._-]+")
    user_home_windows = re.compile("C:" + r"\\+" + "Users" + r"\\+[A-Za-z0-9._-]+", re.IGNORECASE)
    file_extensions = {".md", ".json", ".yaml", ".yml", ".py", ".sh", ".js"}
    excluded_parts = {".git", ".arness", "node_modules", "dist", "build", "__pycache__", "assets", ".aider.chat.history.md"}

    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in file_extensions:
            continue
        if excluded_parts.intersection(path.relative_to(REPO_ROOT).parts):
            continue
        text = validator.read_text(path)
        for pattern in (user_home_unix, user_home_linux, user_home_windows):
            match = pattern.search(text)
            validator.check(match is None, path, f"user-specific absolute path found: {match.group(0) if match else ''}")


REQUIRED_COPILOT_PROMPTS = {
    "arn-brainstorming.prompt.md",
    "arn-planning.prompt.md",
    "arn-implementing.prompt.md",
    "arn-shipping.prompt.md",
    "arn-reviewing-pr.prompt.md",
    "arn-assessing.prompt.md",
    "arn-infra-wizard.prompt.md",
    "arn-code-taskify.prompt.md",
    "arn-code-ship.prompt.md",
}

COPILOT_DOC_PATHS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / ".github/copilot-instructions.md",
    REPO_ROOT / "plugins/arn-code/README.md",
    REPO_ROOT / "plugins/arn-spark/README.md",
    REPO_ROOT / "plugins/arn-infra/README.md",
]

COPILOT_DOC_BAD_PHRASES = [
    "Copilot marketplace",
    "plugin manifest",
    "Copilot plugin manifest",
]

COPILOT_SLASH_EXAMPLES = [
    "/arn-brainstorming",
    "/arn-planning",
    "/arn-implementing",
    "/arn-shipping",
    "/arn-reviewing-pr",
    "/arn-assessing",
    "/arn-infra-wizard",
    "/arn-code-taskify",
    "/arn-code-ship",
]


def validate_copilot_support(validator: Validator) -> None:
    instructions = REPO_ROOT / ".github/copilot-instructions.md"
    validator.check(instructions.is_file(), instructions, "GitHub Copilot instructions file is required")

    prompts_dir = REPO_ROOT / ".github/prompts"
    validator.check(prompts_dir.is_dir(), prompts_dir, "Copilot prompts directory is required")
    if prompts_dir.is_dir():
        filenames = {path.name for path in prompts_dir.glob("*.prompt.md")}
        missing = sorted(REQUIRED_COPILOT_PROMPTS - filenames)
        validator.check(not missing, prompts_dir, f"missing Copilot prompt files: {', '.join(missing)}")

    for path in COPILOT_DOC_PATHS:
        text = validator.read_text(path)
        for phrase in COPILOT_DOC_BAD_PHRASES:
            validator.check(phrase not in text, path, f"Copilot docs must not refer to '{phrase}'")

        has_slash_example = any(example in text for example in COPILOT_SLASH_EXAMPLES)
        validator.check(has_slash_example, path, "Copilot docs should include slash-style /arn-... invocation examples")


def validate_ci_configuration(validator: Validator) -> None:
    workflow = REPO_ROOT / ".github/workflows/validation.yml"
    validator.check(workflow.is_file(), workflow, "validation workflow is required")
    if workflow.is_file():
        text = validator.read_text(workflow)
        validator.check("python3 tools/validate_arness.py" in text, workflow, "workflow must run repository validation")
        validator.check("pull_request:" in text, workflow, "workflow must run on pull requests")
        validator.check("push:" in text, workflow, "workflow must run on pushes")


def main() -> int:
    validator = Validator()
    validate_marketplaces(validator)
    skills_by_plugin, agents_by_plugin = validate_skills_and_agents(validator)
    validate_reference_docs(validator, skills_by_plugin, agents_by_plugin)
    all_skill_names = set().union(*skills_by_plugin.values()) if skills_by_plugin else set()
    validate_evals(validator, all_skill_names)
    validate_markdown_links(validator)
    validate_path_hygiene(validator)
    validate_copilot_support(validator)
    validate_ci_configuration(validator)
    return validator.finish()


if __name__ == "__main__":
    sys.exit(main())
