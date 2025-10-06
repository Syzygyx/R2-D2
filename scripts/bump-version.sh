#!/bin/bash

# Version bump script for SITH Simulator
# Usage: ./scripts/bump-version.sh [major|minor|patch]

set -e

# Default to patch if no argument provided
BUMP_TYPE=${1:-patch}

# Extract current version from simulator.html
CURRENT_VERSION=$(grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+' simulator.html | head -1)
echo "Current version: $CURRENT_VERSION"

# Extract major, minor, patch
IFS='.' read -r MAJOR MINOR PATCH <<< "${CURRENT_VERSION#v}"

# Bump version based on type
case $BUMP_TYPE in
  major)
    NEW_MAJOR=$((MAJOR + 1))
    NEW_VERSION="v${NEW_MAJOR}.0.0"
    ;;
  minor)
    NEW_MINOR=$((MINOR + 1))
    NEW_VERSION="v${MAJOR}.${NEW_MINOR}.0"
    ;;
  patch)
    NEW_PATCH=$((PATCH + 1))
    NEW_VERSION="v${MAJOR}.${MINOR}.${NEW_PATCH}"
    ;;
  *)
    echo "Invalid bump type. Use: major, minor, or patch"
    exit 1
    ;;
esac

echo "New version: $NEW_VERSION"

# Update version in all files
echo "Updating version in files..."

# List of files to update
FILES=(
  "simulator.html"
  "simulator-goldenlayout.html"
  "viewer-fbx.html"
  "python.html"
  "demos.html"
  "help.html"
)

for file in "${FILES[@]}"; do
  if [ -f "$file" ] && grep -q "version-badge" "$file"; then
    echo "Updating $file..."
    sed -i.bak "s/v[0-9]\+\.[0-9]\+\.[0-9]\+/$NEW_VERSION/g" "$file"
    rm "$file.bak"
  fi
done

echo "Version updated to $NEW_VERSION"
echo "Files updated:"
git diff --name-only

echo ""
echo "To commit these changes:"
echo "git add -A"
echo "git commit -m \"Bump version to $NEW_VERSION\""
echo "git push"