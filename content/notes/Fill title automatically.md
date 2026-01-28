---
category: 1.2-web-development-and-tools
title:
date: 2026-01-21 15:08:00 +09:00
colors:
tags:
  - hugo
  - frontmatter
metaRSS: false
draft: false
---

Part of my custom build script automatically generates `title` fields for posts using the filename.

What it does:
- Scans each markdown file's frontmatter for a title field
- If the title is missing or empty, derives a human-readable title from the filename
	- `my-awesome-post.md` → "My awesome post" 
	- `topic---subtopic.md` → "Topic - subtopic"

When making new files in Obsidian, I tend to use the title of the note as a filename, without explicitly setting it in the frontmatter. I used to have a partial in Hugo that falls back to using the filename, but I ended having to use it in too many places. By handling it with a script, there are now fewer edge-cases in my templates.
