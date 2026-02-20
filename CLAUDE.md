# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Toy Skills** is a collection of AI agent skills following the [Agent Skills](https://agentskills.io/) format. Skills are packaged instructions and scripts that extend agent capabilities for Claude Code, Cursor, and OpenCode.

### Architecture

```
skills/
├── <skill-name>/
│   ├── SKILL.md              # Agent instructions (YAML frontmatter + markdown)
│   ├── README.md             # Skill documentation (optional)
│   ├── package.json          # Dependencies (optional)
│   ├── .cursorrules          # Cursor-specific rules (optional)
│   ├── .opencode-rules       # OpenCode-specific rules (optional)
│   └── scripts/              # Helper scripts (optional)
│       └── *.py              # Python utilities
```

**Key Pattern**: Each skill is self-contained with its own SKILL.md that defines:
- YAML frontmatter: `name`, `description`
- Markdown content: Instructions for the agent
- Optional scripts in `scripts/` directory for automation

## Skill Development

### Creating a New Skill

1. Create directory: `skills/<skill-name>/`
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

## Common Commands

### Installation

```bash
# Install a specific skill
npx skills add wvlvik/toy-skills --skill <skill-name>

# Available skills:
# - commit-review      : WeChat Mini Program code review
# - example-skill      : Skill template
# - jimeng-api-image-gen : AI image generation (v1.0.2)
# - jimeng-api-video-gen : AI video generation (v1.0.0)
```

### Development

```bash
# View skill structure
ls -la skills/<skill-name>/

# Edit skill instructions
vim skills/<skill-name>/SKILL.md

# Test Python scripts
python skills/<skill-name>/scripts/<script-name>.py --help
```

### Git Workflow

```bash
# Check status
git status

# Stage changes
git add skills/<skill-name>/

# Commit with message
git commit -m "Update <skill-name> skill"

# Push to remote
git push origin main
```

## Available Skills

| Skill | Description | Version |
|-------|-------------|---------|
| `commit-review` | WeChat Mini Program native development code review | - |
| `example-skill` | Template skill demonstrating structure and format | - |
| `jimeng-api-image-gen` | AI image generation using Volcengine Jimeng API 4.0 | v1.0.2 |
| `jimeng-api-video-gen` | AI video generation using Volcengine Jimeng Video 3.0 Pro | v1.0.0 |

## Key Files

- `README.md` - Project overview and installation
- `AGENTS.md` - Supported agents and compatibility
- `skills/*/SKILL.md` - Individual skill instructions
- `skills/*/scripts/` - Automation scripts (Python)

## Important Patterns

### Environment Variables

Skills use environment variables for configuration:
- `VOLC_ACCESSKEY` / `VOLC_SECRETKEY` - Volcengine API credentials
- `JIMENG_API_URL` - Image API endpoint
- `JIMENG_API_TIMEOUT` - Image API request timeout
- `JIMENG_VIDEO_API_URL` - Video API endpoint
- `JIMENG_VIDEO_API_TIMEOUT` - Video API request timeout

### Error Handling

- Python scripts should validate inputs and provide clear error messages
- API errors should be caught and reported with error codes
- Timeouts should be configurable via environment variables

### Multi-Agent Support

Skills must work across:
- Claude Code (primary)
- Cursor (with .cursorrules)
- OpenCode (with .opencode-rules)

Each agent may have specific rules files for customization.

## Testing Skills

1. **Manual Testing**: Run scripts directly with test inputs
2. **Agent Testing**: Use the skill in Claude Code/Cursor and verify output
3. **Error Cases**: Test with invalid inputs, missing credentials, timeouts

## Deployment

Skills are installed via `npx skills add` from the GitHub repository. Ensure:
- SKILL.md is properly formatted with YAML frontmatter
- Scripts are executable and handle errors
- Documentation is clear and complete
- All dependencies are listed in package.json

## Skill Release Workflow

Use the `skill-release` skill to sync skills from `.agents/skills/` (development) to `skills/` (release) directory with automatic version bumping.

### Quick Commands

```bash
# Release all skills with changes
python3 .agents/skills/skill-release/scripts/release_skill.py

# Preview changes without executing
python3 .agents/skills/skill-release/scripts/release_skill.py --dry-run

# Release specific skill only
python3 .agents/skills/skill-release/scripts/release_skill.py --skill <skill-name>
```

> **Note**: Use `python3` instead of `python` on macOS/Linux systems where `python` is not aliased.

### Release Workflow

1. **Develop** skills in `.agents/skills/<skill-name>/`
2. **Test** the skill locally
3. **Release** using the script (copies to `skills/`, bumps version, commits, pushes)
4. **Install** via `npx skills add wvlvik/toy-skills --skill <skill-name>`

### Version Management

- Version stored in `skills/<skill-name>/version.txt`
- Format: semver (`major.minor.patch`)
- First release: `1.0.0`
- Updates: patch bump (`1.2.3` → `1.2.4`)

### Notes

- `skill-release` itself is excluded from release
- Only skills with SKILL.md are processed
- Unchanged skills are skipped
- Git operations require clean working directory
