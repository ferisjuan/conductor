# Conductor Setup Guide with UV and Versioning

## 📁 Complete File Structure

```
conductor/
├── .github/
│   └── workflows/
│       └── release.yml          # Automated release workflow
├── scripts/
│   └── bump_version.sh          # Version bumping script
├── conductor.py                 # Main script
├── setup.py                     # Setup wizard
├── version.py                   # Version checking utilities
├── update.py                    # Update script
├── install.sh                   # Installation script
├── pyproject.toml              # Project metadata & dependencies (uv)
├── requirements.txt            # Legacy pip requirements
├── README.md                   # Documentation
├── CHANGELOG.md               # Version history
├── LICENSE                    # MIT License
└── .gitignore                # Git ignore rules
```

## 🚀 Initial Setup Steps

### 1. Create Repository

```bash
# Create new repo on GitHub first, then:
git clone https://github.com/ferisjuan/conductor.git
cd conductor

# Add all your files
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Set Up for UV

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment (optional for development)
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install in development mode
uv pip install -e .
```

## 🔄 Version Management Workflow

### Releasing a New Version

```bash
# Make your changes, commit them
git add .
git commit -m "feat: add new feature"

# Bump version (patch, minor, or major)
chmod +x scripts/bump_version.sh
./scripts/bump_version.sh patch

# This script will:
# 1. Update version in pyproject.toml
# 2. Update version in version.py
# 3. Update CHANGELOG.md
# 4. Create git commit
# 5. Create git tag

# Push changes and tag
git push origin main
git push origin v1.0.1

# GitHub Actions will automatically:
# 1. Build the package
# 2. Create GitHub release
# 3. Upload artifacts
# 4. (Optional) Publish to PyPI
```

### Manual Version Bump

If you prefer manual control:

```bash
# 1. Edit pyproject.toml
version = "1.0.1"

# 2. Edit version.py
__version__ = "1.0.1"

# 3. Update CHANGELOG.md
## [v1.0.1] - 2024-XX-XX
### Added
- New feature

# 4. Commit and tag
git add pyproject.toml version.py CHANGELOG.md
git commit -m "chore: bump version to v1.0.1"
git tag -a v1.0.1 -m "Release v1.0.1"

# 5. Push
git push origin main
git push origin v1.0.1
```

## 📦 How Version Checking Works

1. **Automatic Checks**: When users run `conductor`, it checks for updates once per day
2. **Version Cache**: Stores last check time in `~/.conductor/.version_cache`
3. **GitHub API**: Fetches latest release from GitHub
4. **User Notification**: Shows update message if newer version available

```python
# In conductor.py, this runs on startup:
from version import check_for_updates, print_update_message

latest_version = check_for_updates()
if latest_version:
    print_update_message(latest_version)
```

## 🔧 Testing Update Flow

### Test Locally

```bash
# 1. Install current version
./install.sh

# 2. Create a new version
./scripts/bump_version.sh patch
git push origin main
git push origin vX.X.X

# 3. Wait for GitHub release to be created

# 4. Downgrade locally (for testing)
cd ~/.conductor
# Manually edit version.py to older version
__version__ = "0.9.0"

# 5. Run conductor - should see update message
conductor

# 6. Test update command
conductor-update
```

## 🎯 GitHub Actions Setup

The release workflow triggers on tags matching `v*.*.*`:

1. **Builds** the package with `uv build`
2. **Creates** GitHub release with changelog
3. **Uploads** distribution files
4. **Optionally** publishes to PyPI (if `PYPI_TOKEN` secret is set)

### Optional: PyPI Publishing

If you want to publish to PyPI:

```bash
# 1. Create PyPI account: https://pypi.org/account/register/

# 2. Generate API token: https://pypi.org/manage/account/token/

# 3. Add to GitHub Secrets:
#    Repository Settings → Secrets → Actions → New repository secret
#    Name: PYPI_TOKEN
#    Value: pypi-AgEIcHl...
```

## 📝 .gitignore

Create a `.gitignore`:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
.env

# UV
.uv/
uv.lock

# Distribution / packaging
dist/
build/
*.egg-info/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# User config (should not be in repo)
config.json

# OS
.DS_Store
Thumbs.db
```

## 🧪 Testing Checklist

Before releasing:

- [ ] `pyproject.toml` version matches `version.py`
- [ ] CHANGELOG.md is updated
- [ ] Installation script works: `bash install.sh`
- [ ] Setup wizard works: `conductor-setup`
- [ ] Branch creation works: `conductor`
- [ ] Update checking works (test with fake old version)
- [ ] Update command works: `conductor-update`
- [ ] GitHub Actions workflow is valid (check `.github/workflows/release.yml`)

## 🎉 User Installation Flow

Once set up, users install with:

```bash
# One-command install
curl -fsSL https://raw.githubusercontent.com/ferisjuan/conductor/main/install.sh | bash

# Setup
conductor-setup

# Use
conductor

# Update anytime
conductor-update
```

## 🐛 Troubleshooting

### "Version check failing"

- Ensure GitHub repo is public
- Check that releases are being created properly
- Verify `GITHUB_REPO` variable in `version.py` is correct

### "Update not working"

- Check that user has proper permissions
- Verify installation method detection in `update.py`
- Test each installation method separately

### "GitHub Actions failing"

- Check workflow syntax
- Verify GitHub token has proper permissions
- Review Actions logs in repository

## 🔐 Security Notes

- `.env` files are never committed (in `.gitignore`)
- API tokens stored with 600 permissions
- No sensitive data in version control
- GitHub secrets for PyPI token

## 📚 Additional Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
