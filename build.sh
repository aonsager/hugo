#!/bin/bash
set -e

# Step 1: Sync from Obsidian vault to /content/
echo "Step 1: Syncing content from Obsidian vault..."
rsync -a --exclude '.*' --exclude '_*' --delete "$CONTENT_SOURCE" content

# Step 2: Move pages to root
echo "Step 2: Moving pages to root..."
mv content/pages/* content/
rmdir content/pages

# Step 3: Rename index.md to _index.md
echo "Step 3: Renaming index.md files to _index.md..."
find content -name "index.md" -execdir mv {} _index.md \;

# Step 4: Pre-build processing (images, page bundles, etc.)
echo "Step 4: Running pre-build image processing..."
python3 prebuild.py

# Step 5: Build Hugo (from /content-processed/)
echo "Step 5: Building Hugo site..."
hugo --contentDir content-processed

echo "Build complete!"
