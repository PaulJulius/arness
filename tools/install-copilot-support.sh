#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./tools/install-copilot-support.sh [--dry-run] [--force] /path/to/target-repo

Install Arness GitHub Copilot support into another repository.

This copies:
  - .github/copilot-instructions.md
  - .github/prompts/*.prompt.md

Options:
  --dry-run    Show what would be copied without changing the target repo.
  --force      Overwrite existing target files.
  --help       Show this help message.
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
repo_root="$(cd "$script_dir/.." >/dev/null 2>&1 && pwd)"

force=false
dry_run=false
args=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help)
      usage
      exit 0
      ;;
    --dry-run)
      dry_run=true
      shift
      ;;
    --force)
      force=true
      shift
      ;;
    --*)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
    *)
      args+=("$1")
      shift
      ;;
  esac
done

if [[ ${#args[@]} -ne 1 ]]; then
  echo "Error: exactly one target repository path is required." >&2
  usage
  exit 1
fi

target_repo="${args[0]}"

if [[ ! -d "$target_repo" ]]; then
  echo "Error: target repository path does not exist or is not a directory: $target_repo" >&2
  exit 1
fi

copilot_root="$repo_root/.github"
target_copilot_root="$target_repo/.github"
target_prompts_dir="$target_copilot_root/prompts"

source_instructions="$copilot_root/copilot-instructions.md"

if [[ ! -f "$source_instructions" ]]; then
  echo "Error: source Copilot instructions file not found: $source_instructions" >&2
  exit 1
fi

copied=()
skipped=()

copy_file() {
  local source_file="$1"
  local target_file="$2"
  if [[ -e "$target_file" && "$force" != true ]]; then
    skipped+=("$target_file")
    echo "Skipping existing file: $target_file"
    return
  fi

  if [[ "$dry_run" == true ]]; then
    copied+=("$target_file")
    echo "Would copy: $source_file -> $target_file"
    return
  fi

  mkdir -p "$(dirname "$target_file")"
  cp -p "$source_file" "$target_file"
  copied+=("$target_file")
  echo "Copied: $source_file -> $target_file"
}

copy_file "$source_instructions" "$target_copilot_root/copilot-instructions.md"

for source_prompt in "$copilot_root"/prompts/*.prompt.md; do
  if [[ ! -f "$source_prompt" ]]; then
    continue
  fi
  target_prompt="$target_prompts_dir/$(basename "$source_prompt")"
  copy_file "$source_prompt" "$target_prompt"
done

summary_mode=""
if [[ "$dry_run" == true ]]; then
  summary_mode="dry-run"
elif [[ "$force" == true ]]; then
  summary_mode="force"
else
  summary_mode="standard"
fi

printf '\nSummary:\n'
printf 'Target repo: %s\n' "$target_repo"
printf 'Mode: %s\n' "$summary_mode"
printf 'Files copied: %s\n' "${#copied[@]}"
if [[ ${#copied[@]} -gt 0 ]]; then
  for file in "${copied[@]}"; do
    printf '  %s\n' "$file"
  done
fi
printf 'Files skipped: %s\n' "${#skipped[@]}"
if [[ ${#skipped[@]} -gt 0 ]]; then
  for file in "${skipped[@]}"; do
    printf '  %s\n' "$file"
  done
fi

printf '\nNext Copilot command to try:\n'
printf '/arn-planning add rate limiting to the API\n'
