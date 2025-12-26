# Conductor Quick Reference

## 🎯 For Repository Maintainers

### Initial Setup

```bash
# 1. Clone and setup
git clone https://github.com/ferisjuan/conductor.git
cd conductor

# 2. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Push to GitHub
git add .
git commit -m "Initial commit"
git push origin main
```

### Release New Version

```bash
# Quick release (automatic)
./scripts/bump_version.sh patch  # or minor, major

# Then push
git push origin main
git push origin v1.0.x

# Done! GitHub Actions handles the rest
```

### Manual Release

```bash
# 1. Update versions
# Edit: pyproject.toml, version.py

# 2. Update CHANGELOG.md
## [v1.0.x] - 2024-XX-XX
### Added
- New feature

# 3. Commit and tag
git add .
git commit -m "chore: bump version to v1.0.x"
git tag -a v1.0.x -m "Release v1.0.x"

# 4. Push
git push origin main
git push origin v1.0.x
```

## 👥 For End Users

### Installation

```bash
curl -fsSL https://raw.githubusercontent.com/ferisjuan/conductor/main/install.sh | bash
```

### First Time Setup

```bash
conductor --setup
```

### Daily Usage

```bash
# In any git repo
conductor -b
# or
conductor --branch
```

### Update

```bash
conductor --update
```

### Check Version

```bash
conductor --version
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | UV project config, version, dependencies |
| `version.py` | Version checking logic |
| `update.py` | Update command implementation |
| `install.sh` | User installation script |
| `conductor.py` | Main application |
| `setup.py` | Setup wizard |
| `CHANGELOG.md` | Version history |
| `.github/workflows/release.yml` | Auto-release on tag |
| `scripts/bump_version.sh` | Version bump helper |

## 🔢 Version Numbering

Following [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.x.x): Breaking changes
- **MINOR** (x.1.x): New features, backwards compatible
- **PATCH** (x.x.1): Bug fixes, backwards compatible

Examples:

- `1.0.0` → `1.0.1`: Bug fix
- `1.0.0` → `1.1.0`: New feature
- `1.0.0` → `2.0.0`: Breaking change

## 🚀 Release Process Flow

```
1. Make changes
   ↓
2. Run: ./scripts/bump_version.sh patch
   ↓
3. Push: git push origin main && git push origin vX.X.X
   ↓
4. GitHub Actions triggers
   ↓
5. Builds package
   ↓
6. Creates GitHub Release
   ↓
7. Users get update notification
   ↓
8. Users run: conductor-update
```

## 🔄 Update Check Flow

```
User runs 'conductor'
   ↓
Check if 24h passed since last check?
   ↓ Yes
Fetch latest version from GitHub
   ↓
Compare with current version
   ↓
Newer version found?
   ↓ Yes
Show update message
   ↓
User runs 'conductor --update'
   ↓
Detect installation method (uv/pip/script)
   ↓
Update using appropriate method
   ↓
Done!
```

## ⚙️ Configuration Locations

| Item | Location |
|------|----------|
| Installation | `~/.conductor-devtools/` |
| Config | `~/.conductor-devtools/config.json` |
| Credentials | `~/.conductor-devtools/.env` |
| Version cache | `~/.conductor-devtools/.version_cache` |
| Commands | `~/.local/bin/conductor*` |

## 🧪 Testing Commands

```bash
# Test installation
bash install.sh

# Test version check
python version.py --check

# Test update (after creating new release)
conductor --update

# Test main flow
conductor --setup
conductor -b
```

## 📦 Installation Methods

| Method | Command | Use Case |
|--------|---------|----------|
| Curl (recommended) | `curl ... \| bash` | End users, quick install |
| UV | `uv pip install git+...` | Developers, modern Python |
| Pip | `pip install git+...` | Traditional Python users |
| Manual | `git clone && uv pip install -e .` | Development, contributors |

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Command not found | Add `~/.local/bin` to PATH |
| Update not working | Check GitHub repo is public |
| Version check failing | Verify internet connection |
| Installation failing | Check Python 3.10+ installed |

## 📞 Support

- Issues: `https://github.com/ferisjuan/conductor/issues`
- Releases: `https://github.com/ferisjuan/conductor/releases`
- Docs: `https://github.com/ferisjuan/conductor#readme`
