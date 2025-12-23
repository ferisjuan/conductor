#!/bin/bash
# Version bumping script for Conductor
# Usage: ./scripts/bump_version.sh [major|minor|patch]

set -e

BUMP_TYPE=${1:-patch}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔢 Conductor Version Bumper${NC}"
echo "================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -f "version.py" ]; then
  echo -e "${RED}Error: Must be run from repository root${NC}"
  exit 1
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep '^version =' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

if [ -z "$CURRENT_VERSION" ]; then
  echo -e "${RED}Error: Could not find current version${NC}"
  exit 1
fi

echo -e "Current version: ${GREEN}v$CURRENT_VERSION${NC}"

# Parse version components
IFS='.' read -r -a VERSION_PARTS <<<"$CURRENT_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"

# Bump version based on type
case "$BUMP_TYPE" in
major)
  MAJOR=$((MAJOR + 1))
  MINOR=0
  PATCH=0
  ;;
minor)
  MINOR=$((MINOR + 1))
  PATCH=0
  ;;
patch)
  PATCH=$((PATCH + 1))
  ;;
*)
  echo -e "${RED}Error: Invalid bump type '$BUMP_TYPE'${NC}"
  echo "Usage: $0 [major|minor|patch]"
  exit 1
  ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo -e "New version:     ${GREEN}v$NEW_VERSION${NC}"
echo -e "Bump type:       ${YELLOW}$BUMP_TYPE${NC}"
echo ""

# Confirm
read -p "$(echo -e ${YELLOW}?)${NC} Proceed with version bump? [y/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo -e "${RED}Aborted${NC}"
  exit 1
fi

echo ""
echo -e "${BLUE}📝 Updating version files...${NC}"

# Update pyproject.toml
sed -i.bak "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml
rm pyproject.toml.bak
echo -e "${GREEN}✓${NC} Updated pyproject.toml"

# Update version.py
sed -i.bak "s/__version__ = .*/__version__ = \"$NEW_VERSION\"/" version.py
rm version.py.bak
echo -e "${GREEN}✓${NC} Updated version.py"

# Update CHANGELOG if it exists
if [ -f "CHANGELOG.md" ]; then
  TODAY=$(date +%Y-%m-%d)
  # Add new version header
  sed -i.bak "1s/^/## [v$NEW_VERSION] - $TODAY\n\n/" CHANGELOG.md
  rm CHANGELOG.md.bak
  echo -e "${GREEN}✓${NC} Updated CHANGELOG.md"
  echo -e "${YELLOW}⚠${NC}  Remember to add release notes to CHANGELOG.md"
fi

echo ""
echo -e "${BLUE}📦 Committing changes...${NC}"

# Git operations
git add pyproject.toml version.py CHANGELOG.md 2>/dev/null || git add pyproject.toml version.py
git commit -m "chore: bump version to v$NEW_VERSION"
echo -e "${GREEN}✓${NC} Committed version bump"

echo ""
echo -e "${BLUE}🏷️  Creating git tag...${NC}"
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"
echo -e "${GREEN}✓${NC} Created tag v$NEW_VERSION"

echo ""
echo "================================"
echo -e "${GREEN}✅ Version bumped successfully!${NC}"
echo ""
echo "Next steps:"
echo "  1. Review the changes: git show"
echo "  2. Push the changes: git push origin main"
echo "  3. Push the tag: git push origin v$NEW_VERSION"
echo ""
echo "This will trigger the GitHub Actions workflow to:"
echo "  - Build the package"
echo "  - Create a GitHub release"
echo "  - Optionally publish to PyPI"
echo ""
