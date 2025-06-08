#!/bin/bash

# Haconiwa Release Script
# Usage: ./scripts/release.sh <version>
# Example: ./scripts/release.sh 0.1.5

set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "❌ Usage: $0 <version>"
    echo "📝 Example: $0 0.1.5"
    exit 1
fi

echo "🚀 Starting release process for version $VERSION"

# Update version in pyproject.toml
echo "📝 Updating pyproject.toml version to $VERSION"
sed -i '' "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# Update latest version in README files
echo "📝 Updating README files with latest version"
sed -i '' "s/最新バージョン**: .*/最新バージョン**: $VERSION/" README_JA.md
sed -i '' "s/Latest Version**: .*/Latest Version**: $VERSION/" README.md

# Build package
echo "📦 Building package"
rm -rf dist/ build/ src/*.egg-info
python -m build

# Upload to PyPI
echo "🔄 Uploading to PyPI"
python -m twine upload dist/*

# Git operations
echo "📋 Committing changes"
git add .
git commit -m "chore: release v$VERSION

- Update version in pyproject.toml
- Update README with latest version
- Build and upload to PyPI"

echo "🏷️ Creating Git tag"
git tag -a "v$VERSION" -m "Release v$VERSION

See CHANGELOG.md for details."

echo "🚀 Pushing changes and tags"
git push origin main
git push origin "v$VERSION"

echo "✅ Release v$VERSION completed successfully!"
echo "📝 Next steps:"
echo "   1. Create GitHub Release at: https://github.com/dai-motoki/haconiwa/releases/new"
echo "   2. Update CHANGELOG.md with new version details"
echo "   3. Verify PyPI release at: https://pypi.org/project/haconiwa/$VERSION/"