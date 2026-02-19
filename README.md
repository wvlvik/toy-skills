# Toy Skills

A collection of skills for AI coding agents. Skills are packaged instructions and scripts that extend agent capabilities.

Skills follow the [Agent Skills](https://agentskills.io/) format.

## Installation

```bash
npx skills add wvlvik/zan-skills
```

## Available Skills

### example-skill

A template skill demonstrating the structure and format for creating new skills.

**Use when:**
- Learning how to create a new skill
- Understanding the skill package structure
- Testing skill integration

## Skill Structure

Each skill contains:

- `SKILL.md` - Instructions for the agent
- `scripts/` - Helper scripts for automation (optional)
- `references/` - Supporting documentation (optional)

## Project Structure

```
zan-skills/
├── README.md           # Project documentation
├── AGENTS.md           # Supported AI agents
├── skills/             # All skills directory
│   └── example-skill/  # Example skill
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
```

## Supported Agents

- Claude Code
- Cursor
- Windsurf

See [AGENTS.md](./AGENTS.md) for details.

## License

MIT
