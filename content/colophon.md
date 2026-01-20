---
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
## How I create this site
### Writing

I write the content of this site in [[Obsidian]]. I'm not _that_ deep in the Obsidian ecosystem, and I don't really use any advanced features, but everything about it, especially PC/Mobile cross-functionality, is pretty good.

### Site generation

This site is built with [Hugo](https://gohugo.io), a static-site generator that transforms a folder of Markdown files into a website. You can see the [source code](https://github.com/aonsager/hugo), or read about my [[hugo|various customizations]].

Because the post files are in my Obsidian vault, I have a script that uses rsync to copy all of the files over to my Hugo repository to rebuild the site. I'm not sure if using symlinks would have been a better solution, but this works just fine.

The contents are pushed to Github – mostly as a backup. Then, the script rsync the generated site to my VPS.

Since the Markdown content is synced via iCloud, I could even set up a cron task on my home computer to build + deploy every hour. For now though, I write posts infrequently enough that manual pushes are fine.

### Hosting

I have a small VPS through [Hetzner](https://www.hetzner.com) which is good enough to host:

- This site
- [Pokemon Fusion](https://pokemon.alexonsager.net/)
- My [GoToSocial](https://gotosocial.org/) [instance](https://gts.invisibleparade.com/@alex) for participating in the Fediverse
- [Goat Counter](https://www.goatcounter.com) for simple analytics
- Any other small project I'm playing with

## Site architecture

I'm aiming to create a comfortable [[horizontal architecture]] for the site. That said, the content is divided into a number of major sections:

- [Pages](/pages) is an index of my various [slash pages](https://slashpages.net/)
- [Blog posts](/posts) where I put some effort into making my thoughts public
- [Links](/links) where I share cool things I've found
- [Notes](/notes) where I compile information that might be useful or interesting later
- [Micro](/micro) is an archive of my Fediverse posts

I've put some functions together in an aim to make navigation across these sections as seamless and natural as possible.

### Related posts

At the end of each post, there is a list of up to 5 related posts. These are determined by how many tags the posts have in common. 

I used to just show a list of posts, but now I display which tags are held in common. I think this is a nice way to make it easier for the reader to decide if they are interested.

### Tag pages

Each tag has a page that lists all posts that contain that tag. Instead of a just a simple list, I've also arranged these pages to prioritize pages with strong connections to each other. You can also see which tags are commonly used together.

## Design decisions

### Colors

The colors I use on this site are based on the [Base16 – Eighties](https://github.com/chriskempson/base16-default-schemes) color scheme by Chris Kempson. These are the colors I use in my text editors, and I find them very comfortable – hopefully you do, too.

### Post colors

To add some extra color to these pages, I automatically generate 5 colors based on the content of the post and use them as an accent. You can read about how I do that [[adding-color-to-posts-automatically|here]].

