# Skill Release

Sync and publish skills from `.agents/skills/` to `skills/` directory with version bumping and git automation.

## Features

- Change detection using content hash
- Automatic version bumping (semver patch)
- Git automation (add, commit, push)
- Dry-run preview mode
- Selective skill release

## Usage

### Release All Skills

```bash
scripts/release_skill.py
```

### Preview Changes (Dry-Run)

```bash
scripts/release_skill.py --dry-run
```

### Release Specific Skill

```bash
scripts/release_skill.py --skill jimeng-api-image-gen
```

## Workflow

1. Scan `.agents/skills/` for all skills with SKILL.md
2. Compare with `skills/` directory using content hash
3. Copy changed skills, creating/updating `version.txt`
4. Run `git add . && git commit -m "chore: release skills" && git push`

## Version Management

Version is stored in `version.txt` at skill root:

```
skill-name/
├── SKILL.md
├── version.txt    # e.g., "1.2.3"
└── scripts/
```

- First release: `1.0.0`
- Updates: patch bump (`1.2.3` → `1.2.4`)

## Project Structure

```
project/
├── .agents/skills/     # Development source
│   ├── skill-a/
│   └── skill-b/
└── skills/             # Release destination
    ├── skill-a/
    │   ├── SKILL.md
    │   └── version.txt
    └── skill-b/
        ├── SKILL.md
        └── version.txt
```

## Requirements

- Python 3.8+
- Git repository with push access
- `.agents/skills/` and `skills/` directories

## Notes

- `skill-release` itself is excluded from release
- Only skills with SKILL.md are processed
- Unchanged skills are skipped
