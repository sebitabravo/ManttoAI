#!/usr/bin/env bash
set -euo pipefail

npx skills add mindrally/skills --skill fastapi-python --skill playwright -a claude-code -a opencode -a codex -a cursor -a gemini-cli -a github-copilot -y
npx skills add obra/superpowers --skill systematic-debugging --skill test-driven-development --skill verification-before-completion --skill writing-plans -a claude-code -a opencode -a codex -a cursor -a gemini-cli -a github-copilot -y
npx skills add wshobson/agents --skill api-design-principles --skill code-review-excellence --skill python-testing-patterns --skill python-performance-optimization -a claude-code -a opencode -a codex -a cursor -a gemini-cli -a github-copilot -y
npx skills add github/awesome-copilot --skill git-commit --skill documentation-writer -a claude-code -a opencode -a codex -a cursor -a gemini-cli -a github-copilot -y
