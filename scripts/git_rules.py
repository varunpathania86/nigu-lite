"""Git conventions from master-plan.md §11.5, shared by local hooks and CI."""

from __future__ import annotations

import re

BRANCH_PREFIXES = ("feature", "bugfix", "hotfix", "patch", "tenant", "docs", "chore")
PROTECTED_BRANCHES = ("main",)
MAX_SUBJECT = 72

_BRANCH_RE = re.compile(rf"^({'|'.join(BRANCH_PREFIXES)})/[a-z0-9][a-z0-9._-]*$")
_TYPE_PREFIX_RE = re.compile(r"^[a-zA-Z]+(\([^)]*\))?!?:\s|^\([a-zA-Z]+\)")
_AI_COAUTHOR_RE = re.compile(
    r"^co-authored-by:.*\b(copilot|roo|claude|anthropic|openai|chatgpt|codex|gemini|cursor|"
    r"aider|devin|codeium|windsurf|tabnine)\b",
    re.IGNORECASE,
)


def check_branch(name: str) -> list[str]:
    if name in PROTECTED_BRANCHES or _BRANCH_RE.match(name):
        return []
    prefixes = ", ".join(f"{p}/" for p in BRANCH_PREFIXES)
    return [f"Branch '{name}' must be '<prefix>/<lowercase-slug>' with prefix one of: {prefixes}"]


def check_subject(subject: str) -> list[str]:
    """Rules for a commit subject or PR title."""
    if not subject.strip():
        return ["Message is empty"]
    errors = []
    if len(subject) > MAX_SUBJECT:
        errors.append(f"Subject has {len(subject)} characters; maximum is {MAX_SUBJECT}")
    if _TYPE_PREFIX_RE.match(subject):
        errors.append("No type prefixes or scopes such as 'feat:', 'fix(edu):' or '(feat)'")
    elif not subject[0].isupper():
        errors.append("Subject must start with a capital letter")
    if subject.endswith("."):
        errors.append("Subject must not end with a period")
    return errors


def check_message(message: str) -> list[str]:
    lines = [line for line in message.splitlines() if not line.startswith("#")]
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return ["Message is empty"]
    errors = check_subject(lines[0].rstrip())
    if len(lines) > 1 and lines[1].strip():
        errors.append("Leave a blank line between the subject and the body")
    if any(_AI_COAUTHOR_RE.match(line.strip()) for line in lines):
        errors.append("Remove 'Co-authored-by' trailers for AI tools; human co-authors are fine")
    return errors
