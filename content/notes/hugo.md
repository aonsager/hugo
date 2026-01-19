---
title: Hugo
date: 2026-01-16 22:32:00 +09:00
colors:
tags:
  - hugo
  - blog
  - coding
  - customization
metaRSS: false
draft: false
---

This blog is built using [Hugo](https://gohugo.io). I've described my motivations in [[static-site-generator-wishlist | this post]] but the main points are:

1. Can be expected to keep working without maintenance (minimal dependencies)
2. Easy enough to customize for my needs
3. Without adding Hugo-specific code to my markdown files

The first point was a given because Hugo is written in Go, but I needed to do a fair bit of experimentation to see how 2 and 3 hold up. This is a growing list of things I have learned about Hugo, and specific ways I have customized it.

You can also look at the source code for this site [here](https://github.com/aonsager/hugo).

- [[Custom markdown parsing in Hugo]]
- [[Supporting wikilinks in Hugo]]
- [[Show full page contents on folder page]]
- [[Customize display of internal and external links]]
- [[Show related posts]]
- [[Show correlated posts on tag pages]]
