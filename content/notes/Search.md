---
category: 1.2-web-development-and-tools
title:
date: 2026-01-25 22:09:00 +09:00
colors:
tags:
  - search
  - fusejs
  - websites
  - indexing
  - shortcuts
  - performance
metaRSS: false
---
I'm very happy with the way search is working on my site.

The search is powered by [Fuse.js](https://www.fusejs.io) which gives full-text search over all of my pages. It defaults to just using the first ~300 characters of the post as a snippet, but I figure I have few enough pages that I can index the full text without much issue. Results are displayed very quickly.

I've also added the `/` shortcut. I wanted to support `⌘`/`ctrl` + `K` as well, but apparently that's the default shortcut in Firefox to focus the address bar, and I didn't want to overwrite that.
