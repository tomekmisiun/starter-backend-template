#!/usr/bin/env bash
set -euo pipefail

msg_file="${1:?commit message file required}"

if grep -Eiq '^(Co-authored-by|Authored-by):.*(cursor|codex|claude|openai|anthropic|github copilot)' "$msg_file"; then
  cat <<EOF
ERROR: AI authorship trailers are not allowed in commit messages.
Remove Co-authored-by / Authored-by lines for agent tools.
EOF
  exit 1
fi
