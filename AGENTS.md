# Supported AI Agents

This skill package is designed to work with various AI coding agents. Below is the list of supported agents:

## Fully Supported

- **Claude Code** - Anthropic's coding-capable AI model
- **Cursor** - AI-powered code editor
- **OpenCode** - AI-powered code editor

## Compatibility Notes

Each skill may have specific agent compatibility notes. Check individual `SKILL.md` files for details.

## Getting Started

Install this skill package using the skills CLI:

```bash
npx skills add wvlvik/zan-skills --skill <skill-name>
```

Once installed, skills will be automatically available in supported agents.

## Releasing Skills

To release skills from `.agents/skills/` to `skills/` directory:

```bash
# Preview changes
python3 .agents/skills/skill-release/scripts/release_skill.py --dry-run

# Execute release (copy, version bump, git commit & push)
python3 .agents/skills/skill-release/scripts/release_skill.py
```

> **Note**: Use `python3` instead of `python` on macOS/Linux systems where `python` is not aliased.
