#!/usr/bin/env bash
# Local PR review using MiniMax M2.7
# Usage: ./scripts/review.sh [pr-number] [base-branch]
# Example: ./scripts/review.sh 12 main
# If pr-number is provided, the review will be posted as a PR comment.
set -euo pipefail

PR_NUMBER="${1:-}"
BASE="${2:-main}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Load API key
if [ -f "$ROOT_DIR/.env" ]; then
  source "$ROOT_DIR/.env"
fi
if [ -z "${MINIMAX_API_KEY:-}" ]; then
  echo "MINIMAX_API_KEY not set. Add it to .env"
  exit 1
fi

# Get diff
DIFF=$(git diff "$BASE"...HEAD)
if [ -z "$DIFF" ]; then
  echo "No changes vs $BASE"
  exit 0
fi

# Truncate diff if too large (MiniMax context limit)
DIFF_LINES=$(echo "$DIFF" | wc -l)
if [ "$DIFF_LINES" -gt 3000 ]; then
  DIFF=$(echo "$DIFF" | head -3000)
  DIFF="$DIFF
... (truncated, ${DIFF_LINES} total lines)"
fi

echo "Reviewing $(echo "$DIFF" | wc -l) lines of diff against $BASE..."
echo ""

# Build prompt
SYSTEM_PROMPT='You are an expert code reviewer for a Python project (open_intern — an AI employee framework). Review the git diff below.

## Review Checklist

### Code Quality
- Are there potential bugs or logic errors?
- Is error handling appropriate (not too broad, not missing)?
- Are there unnecessary complexity or over-engineering?
- Are there duplicated code blocks that should be extracted?

### Python Conventions
- Are type annotations present and correct?
- Are Pydantic models properly defined?
- Does the code follow PEP 8 / ruff conventions?
- Are imports organized (stdlib → third-party → local)?

### Architecture
- Is the separation of concerns maintained (core/memory/safety/integrations)?
- Are async patterns used correctly?
- Is the config system used properly (no hardcoded values)?

### Security
- Are user inputs properly validated?
- Are API keys and secrets handled securely (not hardcoded, not logged)?
- Are SQL queries parameterized (no injection)?

## Instructions
- For each issue, reference the file and line, explain WHY it is a problem, and suggest a concrete fix.
- Prioritize: bugs > security > correctness > readability > style.
- Do NOT comment on things that are already clean and readable.
- If there are no issues, say "LGTM" with a brief summary of what the code does.'

# Call MiniMax API (use temp files to avoid shell argument size limits)
TMPDIR_REVIEW=$(mktemp -d)
trap 'rm -rf "$TMPDIR_REVIEW"' EXIT

# Pre-encode diff as JSON string to handle control characters
echo "$DIFF" | jq -Rs '.' > "$TMPDIR_REVIEW/diff.json"
echo "$SYSTEM_PROMPT" | jq -Rs '.' > "$TMPDIR_REVIEW/system.json"

PAYLOAD=$(jq -n \
  --slurpfile system "$TMPDIR_REVIEW/system.json" \
  --slurpfile diff "$TMPDIR_REVIEW/diff.json" \
  '{
    model: "MiniMax-M2.7",
    messages: [
      {role: "system", content: $system[0]},
      {role: "user", content: ("Review this diff:\n\n```diff\n" + $diff[0] + "\n```")}
    ],
    max_tokens: 8192
  }')

RESPONSE=$(curl -s https://api.minimaxi.chat/v1/chat/completions \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# Extract content
ERROR=$(echo "$RESPONSE" | jq -r '.error.message // empty' 2>/dev/null)
if [ -n "$ERROR" ]; then
  echo "MiniMax API error: $ERROR"
  exit 1
fi

CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // empty' 2>/dev/null)
if [ -z "$CONTENT" ]; then
  echo "Empty response from MiniMax"
  echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
  exit 1
fi

# Strip <think>...</think> tags (MiniMax reasoning)
CONTENT=$(echo "$CONTENT" | sed '/<think>/,/<\/think>/d')

TOKENS=$(echo "$RESPONSE" | jq -r '.usage.total_tokens // "?"' 2>/dev/null)

# Print to terminal
echo "--------------------------------------------"
echo "MiniMax M2.7 Code Review"
echo "--------------------------------------------"
echo ""
echo "$CONTENT"
echo ""
echo "--------------------------------------------"
echo "tokens: $TOKENS"

# Post to PR if pr-number provided
if [ -n "$PR_NUMBER" ]; then
  COMMENT_BODY="## MiniMax M2.7 Code Review

$CONTENT

---
<sub>tokens: $TOKENS | reviewed locally via \`scripts/review.sh\`</sub>"

  gh pr comment "$PR_NUMBER" --body "$COMMENT_BODY"
  echo ""
  echo "Review posted to PR #$PR_NUMBER"
fi
