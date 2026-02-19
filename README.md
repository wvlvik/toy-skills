# Toy Skills

A collection of skills for AI coding agents. Skills are packaged instructions and scripts that extend agent capabilities.

Skills follow the [Agent Skills](https://agentskills.io/) format.

## Installation

```bash
npx skills add wvlvik/toy-skills --skill <skill-name>
```

## Available Skills

### commit-review

WeChat Mini Program native development code review skill for checking architecture constraints, best practices, and common issues.

**Use when:**
- Before committing code (pre-git commit)
- During code review
- When user explicitly requests code review
- Keywords: review, 评审, 检查, commit, 提交

**Features:**
- Runtime module externalization check
- Dependency installation rule validation (devDependencies)
- TypeScript enforcement check
- Tailwind CSS compliance validation
- Performance best practices check
- Common issues detection (iOS compatibility, etc.)

### jimeng-api-image-gen

Generate high-quality AI images using Volcengine Jimeng API 4.0.

**Use when:**
- Text-to-image generation requests
- Image-to-image editing or style transfer
- Batch image creation
- Keywords: generate image, create picture, AI image, 即梦, Jimeng, Seedream

**Features:**
- Text-to-image generation
- Image-to-image editing
- Multiple resolution presets (1K, 2K, 4K)
- Custom dimensions and aspect ratios
- Local file output support

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
toy-skills/
├── README.md              # Project documentation
├── AGENTS.md              # Supported AI agents
├── skills/                # All skills directory
│   ├── commit-review/     # WeChat Mini Program code review
│   │   └── SKILL.md
│   ├── jimeng-api-image-gen/  # Jimeng AI image generation
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   └── scripts/
│   └── example-skill/     # Example skill template
│       └── SKILL.md
```

## Supported Agents

- Claude Code
- Cursor
- Windsurf

See [AGENTS.md](./AGENTS.md) for details.

## License

MIT
