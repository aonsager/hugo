# Copy files from Obsidian vault
rsync -av --exclude '.*' --exclude '_*' --delete "$CONTENT_SOURCE" content

# Pages contained within pages/ are moved to root
mv content/pages/* content/
rmdir content/pages

# Pages named index.md are renamed to _index.md
find . -name "index.md" -execdir mv {} _index.md \;
