# Supported AI Agents

This skill package is designed to work with various AI coding agents. Below is the list of supported agents:

## Fully Supported

- **Claude Code** - Anthropic's coding-capable AI model
- **Cursor** - AI-powered code editor
- **OpenCode** - AI-powered code editor
- **Windsurf** - AI-powered code editor

## Compatibility Notes

Each skill may have specific agent compatibility notes. Check individual `SKILL.md` files for details.

## Getting Started

Install this skill package using the skills CLI:

```bash
npx skills add wvlvik/toy-skills --skill <skill-name>
```

Once installed, skills will be automatically available in supported agents.

## Available Skills

| Skill | Description | Version |
|-------|-------------|---------|
| `commit-review` | WeChat Mini Program native development code review | - |
| `example-skill` | Template skill demonstrating structure and format | - |
| `jimeng-api-image-gen` | AI image generation using Volcengine Jimeng API 4.0 | v1.0.2 |
| `jimeng-api-video-gen` | AI video generation using Volcengine Jimeng Video 3.0 Pro | v1.0.0 |

## Skill Development

### Creating a New Skill

1. Create directory: `.agents/skills/[skill-name]/`
2. Create `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: skill-name
   description: Brief description of what the skill does
   ---
   ```
3. Add markdown instructions for the agent
4. Add `scripts/` directory if automation is needed
5. Add `package.json` if dependencies are required

### SKILL.md Format

- **YAML Frontmatter**: Metadata (name, description)
- **Markdown Content**: Agent instructions with:
  - Quick Start section with command examples
  - Configuration details
  - Error handling
  - Reference documentation

### Python Scripts

Scripts in `skills/<skill-name>/scripts/` should:
- Be executable and well-documented
- Use environment variables for configuration
- Support `--help` flag
- Handle errors gracefully
- Output results in clear format (JSON, markdown, or plain text)

Example: `scripts/generate_image.py` uses Volcengine API with IAM v4 signature authentication.

## Releasing Skills

To release skills from `.agents/skills/` to `skills/` directory:

```bash
# Preview changes
python3 .agents/skills/skill-release/scripts/release_skill.py --dry-run

# Execute release (copy to skills/, git commit & push)
python3 .agents/skills/skill-release/scripts/release_skill.py

# Release specific skill only
python3 .agents/skills/skill-release/scripts/release_skill.py --skill <skill-name>
```

> **Note**: Use `python3` instead of `python` on macOS/Linux systems where `python` is not aliased.

## Project Structure

```
toy-skills/
├── .agents/skills/         # Development source
│   ├── jimeng-api-image-gen/
│   ├── jimeng-api-video-gen/
│   └── skill-release/      # Release automation tool
├── skills/                 # Release destination
│   ├── commit-review/
│   ├── example-skill/
│   ├── jimeng-api-image-gen/   # v1.0.2
│   └── jimeng-api-video-gen/   # v1.0.0
├── AGENTS.md
├── CLAUDE.md
└── README.md
```
