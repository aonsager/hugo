---
aliases:
  - Colophon
title: Colophon
date: 2025-12-24 12:37:00 +09:00
colors:
  - "#939493"
  - "#acc099"
  - "#b5b6b1"
  - "#aeabaa"
  - "#bcbbbd"
tags:
  - quartz
  - obsidian
  - markdown
  - website
  - icloud
  - colophon
---
This site is build with #quartz (https://quartz.jzhao.xyz), which is a static-site generator that transforms a folder of Markdown files into a website. 

It's designed to work well with #obsidian (https://obsidian.md) 's features, and that is what I use to write my content. I'm not _that_ deep in the Obsidian ecosystem, and I don't really use any advanced features, but everything about it, especially PC/Mobile cross-functionality, is pretty good.

Because I access my Obsidian Vault on both desktop and mobile, the vault is saved in a weird location in my iCloud drive:

```
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/
```

When building this site with Quartz, I have a script that batch-copies the files from my Obsidian vault into the Quartz folder, which it then uses to generate the site. The generated site is pushed to Github, where I have an Action setup to copy the contents of the `public/` folder to my VPS.

I've always felt that it's unwieldy to install static-site generators on the VPS, so I prefer to do the generation on my local machine and just copy over the outputted files.

Since the Markdown content is synced via iCloud, I can even set up a cron task on my home computer to build + deploy every hour.

I've also tagged various files with #colophon that explain small features I've added.
